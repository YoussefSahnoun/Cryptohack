from pwn import *
from Crypto.Random import random
import json
from randcrack import RandCrack
from gmpy2 import iroot
VALUES = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six',
          'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King']
SUITS = ['Clubs', 'Hearts', 'Diamonds', 'Spades']


class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __str__(self):
        return f"{self.value} of {self.suit}"

    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return VALUES.index(self.value) > VALUES.index(other.value)

        
DECK=[Card(value, suit) for suit in SUITS for value in VALUES]
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(b, n):
    g, x, _ = egcd(b, n)
    if g == 1:
        return x % n

 
def solve_lcg_parameters(observed, m=2**61 - 1):
    print(observed)
    X1, X2, X3 = observed[:3]

    mul = (X3 - X2) * modinv(X2 - X1, m) % m

    inc = (X2 - X1 * mul) % m

    

    return mul, inc



def predict_next(X, mul, inc, m=2**61 - 1):
    return (X * mul + inc) % m

def rebase(n, b=52):
        if n < b:
            return [n]
        else:
            return [n % b] + rebase(n//b, b)

def unrebase(observed):
    x=0
    for i in range(len(observed)):
        x+=observed[i]*(52**i)
    return x


def inx(card,D=DECK):
	for i in range(len(D)):
		if D[i].value==card.value and D[i].suit==card.suit:
			return i


r=remote("socket.cryptohack.org" ,13383)
observed=[]
seeds_count=0
seeds=[]
num_deal=-1
i=1
next_indexes=[]
while True:
	response=json.loads(r.recvline().strip().decode())
	if response['round']==200:
		break
	current_card_value=response['hand'].split(' ')[0]
	current_card_suit=response['hand'].split(' ')[2]
	current_card=Card(current_card_value,current_card_suit)
	print(response)
	observed.insert(0,inx(current_card))
	print("observed:",observed)
	if i==int(num_deal):#if we have all the seed
		seeds.append(unrebase(observed))#unrebase the observation to get the actual number and add it to the seed
		seeds_count+=1
		if len(seeds)>=3:#if we have 3 seeds
			print("SEEDS: ",seeds)
            #we predict the next seed after solving the lcg and we rebase the result to 
            #the array next_indexes
			next_indexes=rebase(predict_next(seeds[-1], solve_lcg_parameters(seeds)[0],solve_lcg_parameters(seeds)[1]))
			print("THE NEXT INDEX IS:",next_indexes)
			if len(next_indexes)==num_deal:
				print("TRUE")
			else:
				print("FALSE")
		observed=[]#we empty observed array
		i=0
    #the next code is to extract the number of deals before reshuffeling again
    #which is the length of our next observation
	if 'reshuffle'in response['msg']:
		if 'Welcome' in response['msg'] :
			num_deal=response['msg'].split(' ')[20]
		else:
			num_deal=response['msg'].split(' ')[13]
	#before we get our 3 seeds we need to guess randomly so let's guess high if it's more likely that we get high
    #and low otherwise
	if seeds_count <3 :
		if len(VALUES[:VALUES.index(current_card.value)])>len(VALUES[VALUES.index(current_card.value):]):
			r.sendline(b'{"choice":"lower"}')
		else:
			r.sendline(b'{"choice":"higher"}')
    #if we have our seeds ready and our next indexes ready we guess based on the last elemnt 
    #of our guessing array
	else:
		print("-----------------got the next indexes------------------")
		next_guess=next_indexes.pop()
		print(f"our current card is {current_card} the next card is {DECK[next_guess]}")
		if VALUES.index(current_card.value) > (next_guess%13) :
			r.sendline(b'{"choice":"lower"}')
		elif VALUES.index(current_card.value) < (next_guess%13):
			r.sendline(b'{"choice":"higher"}')
		else:
			if SUITS.index(current_card.suit) >= SUITS.index(DECK[next_guess].suit):
				r.sendline(b'{"choice":"lower"}')
			else:
				r.sendline(b'{"choice":"higher"}')

	i+=1
	
	
r.sendline(b'{"choice":"higher"}')
print(r.recvline())