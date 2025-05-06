import time
import random
import json
import traceback
from datetime import datetime
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from colorama import Fore, Style, init

init(autoreset=True)

# Configuration
RPC_URL = "https://api.mainnet-beta.solana.com"
RATE_LIMIT_REQUESTS = 10  # Number of requests before pause
RATE_LIMIT_PAUSE = 2      # Pause duration in seconds
MAX_RETRIES = 3           # Maximum number of retries for failed requests
RETRY_DELAY = 1           # Delay between retries in seconds
VERBOSE_MODE = True       # Show detailed logs
DETAILED_LOG_FREQUENCY = 10  # Show detailed logs every X attempts

# Initialize client with timeout
client = Client(RPC_URL, timeout=10)

# Statistics
spinner = ['-', '\\', '|', '/']
spin_index = 0
attempts = 0
start_time = time.time()
successful_requests = 0
failed_requests = 0
rate_limited_requests = 0

print(Fore.CYAN + "[*] Scanning for any funded Solana accounts...")
print(Fore.YELLOW + "[*] Using RPC endpoint: " + RPC_URL)
print(Fore.YELLOW + "[*] Rate limiting: Pause for " + str(RATE_LIMIT_PAUSE) + "s after every " + str(RATE_LIMIT_REQUESTS) + " requests")
print(Fore.YELLOW + "[*] Showing behind-the-scenes details to understand the process")

try:
    while True:
        attempts += 1
        
        # Apply rate limiting
        if attempts % RATE_LIMIT_REQUESTS == 0:
            print(f"\n{Fore.CYAN}[RATE LIMIT] Pausing for {RATE_LIMIT_PAUSE}s to avoid rate limits...")
            time.sleep(RATE_LIMIT_PAUSE)
        
        # Generate a random keypair
        keypair = Keypair()
        pubkey = keypair.pubkey()
        pubkey_str = str(pubkey)
        
        # Basic spinner with attempt count
        print(f"\r{Fore.YELLOW}{spinner[spin_index]} {Style.DIM}Checking {pubkey_str} (#{attempts})", end="")
        spin_index = (spin_index + 1) % len(spinner)
        
        # Show detailed information periodically
        show_details = (attempts % DETAILED_LOG_FREQUENCY == 0) or VERBOSE_MODE
        
        # Retry logic
        retries = 0
        success = False
        
        while retries <= MAX_RETRIES and not success:
            request_start_time = time.time()
            
            try:
                # Make the RPC request
                if show_details and retries == 0:
                    print(f"\n{Fore.BLUE}[RPC] Sending request to check balance of {pubkey_str}")
                elif retries > 0:
                    print(f"\n{Fore.YELLOW}[RETRY] Attempt {retries}/{MAX_RETRIES} for {pubkey_str}")
                
                # Use the Pubkey object directly
                response = client.get_balance(pubkey)
                request_time = time.time() - request_start_time
                
                # Extract balance information - handle the new response format
                # The response is now a GetBalanceResp object with a value attribute
                balance_lamports = response.value
                balance_sol = balance_lamports / 1e9
                
                if show_details:
                    print(f"{Fore.GREEN}[RPC] Response received in {request_time:.4f}s: Balance = {balance_lamports} lamports")
                    print(f"{Fore.WHITE}[INFO] Account balance: {balance_sol} SOL ({balance_lamports} lamports)")
                
                successful_requests += 1
                success = True
                
                # If we found a funded account
                if balance_sol > 0:
                    elapsed_time = time.time() - start_time
                    print(f"\n\n{Fore.GREEN}[✔] FOUND FUNDED ACCOUNT: {pubkey_str} with {balance_sol} SOL!")
                    print(f"{Fore.MAGENTA}[🔑] Private key: {keypair.to_bytes().hex()}")
                    print(f"{Fore.BLUE}[📬] Public key: {pubkey_str}")
                    print(f"{Fore.YELLOW}[📊] Found after {attempts} attempts in {elapsed_time:.2f} seconds")
                    print(f"{Fore.YELLOW}[📊] Success rate: {successful_requests/attempts*100:.2f}% ({successful_requests}/{attempts})")
                    break
                    
            except Exception as e:
                request_time = time.time() - request_start_time
                
                # Get detailed error information
                error_type = type(e).__name__
                error_message = str(e)
                
                # Check for common error types
                if "429" in error_message or "Too many requests" in error_message:
                    rate_limited_requests += 1
                    print(f"\n{Fore.RED}[RATE LIMITED] The RPC endpoint is rate limiting us. Pausing...")
                    time.sleep(RATE_LIMIT_PAUSE * 2)  # Longer pause for rate limits
                elif "timeout" in error_message.lower():
                    print(f"\n{Fore.RED}[TIMEOUT] Request timed out after {request_time:.4f}s")
                else:
                    if show_details:
                        print(f"\n{Fore.RED}[ERROR] {error_type}: {error_message}")
                        print(f"{Fore.RED}[ERROR] Request failed after {request_time:.4f}s")
                
                # Decide whether to retry
                if retries < MAX_RETRIES:
                    retries += 1
                    time.sleep(RETRY_DELAY)
                else:
                    failed_requests += 1
                    break
            
        # Show statistics periodically
        if attempts % 50 == 0:
            elapsed_time = time.time() - start_time
            requests_per_second = attempts / elapsed_time if elapsed_time > 0 else 0
            success_rate = (successful_requests / attempts) * 100 if attempts > 0 else 0
            
            print(f"\n{Fore.CYAN}[STATS] Progress update:")
            print(f"{Fore.CYAN}[STATS] Attempts: {attempts} in {elapsed_time:.2f} seconds ({requests_per_second:.2f} req/s)")
            print(f"{Fore.CYAN}[STATS] Success rate: {success_rate:.2f}% ({successful_requests}/{attempts})")
            print(f"{Fore.CYAN}[STATS] Failed requests: {failed_requests}")
            print(f"{Fore.CYAN}[STATS] Rate limited requests: {rate_limited_requests}")
            print(f"{Fore.CYAN}[STATS] Probability of success: Approximately 1 in 2^256 (virtually zero)")
            
            # Add a small pause to make sure stats are visible
            time.sleep(1)

except KeyboardInterrupt:
    elapsed_time = time.time() - start_time
    print(f"\n{Fore.RED}[!] Interrupted by user after {elapsed_time:.2f} seconds")
    print(f"{Fore.RED}[!] Total checked: {attempts} addresses")
    print(f"{Fore.RED}[!] Successful requests: {successful_requests}")
    print(f"{Fore.RED}[!] Failed requests: {failed_requests}")
    print(f"{Fore.RED}[!] Rate limited requests: {rate_limited_requests}")
    if attempts > 0:
        print(f"{Fore.RED}[!] Success rate: {successful_requests/attempts*100:.2f}%")
        print(f"{Fore.RED}[!] Average speed: {attempts/elapsed_time:.2f} addresses per second")
except Exception as e:
    print(f"\n{Fore.RED}[!] Unexpected error: {str(e)}")
    print(traceback.format_exc())

