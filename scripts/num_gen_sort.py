import random
import sys

def main():
    try:
        # Check if command line argument is provided
        if len(sys.argv) != 2:
            print("Usage: python3 num_gen_sort.py <number_of_numbers>")
            return
        
        n = int(sys.argv[1])
        
        if n <= 0:
            print("Please enter a positive integer.")
            return
        
        # Generate n random numbers
        numbers = [random.randint(1, 1000000) for _ in range(n)]
                
        # Sort the numbers
        sorted_numbers = sorted(numbers)
        
        # print(f"\nSorted numbers:")
        # print(sorted_numbers)
        
    except ValueError:
        print("Invalid input! Please enter a valid integer.")
    
if __name__ == "__main__":
    main()