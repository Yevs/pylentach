import sys
import os

# comment
def main(args):
    if args[1] == 'start':
        os.system('python3 pylentach/lentach.py')
    elif args[1] == 'test':
        os.system('python3 -m unittest discover')
    else:
        print('u r wrong. u should feel bad.')


if __name__ == '__main__':
    main(sys.argv)
