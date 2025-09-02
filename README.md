# SSH Honeypot with Emulated Shell

A simple SSH honeypot that emulates a shell environment and logs attacker activity.  


**Development environtment:**

    • Python3.11+
    
    • Virtual studios 
    
 __INSTALLATION__
 

1. Clone the Repository
   
   git clone https://github.com/murariguna/honeypot.git

2. Install Dependencies


    pip install paramiko  # all  the remainig modules are built-n



**USAGE**

Run the honeypot script:

      python honeypot.py

   
By default, it listens on port 2222.
You can connect to it via:


      ssh -p <port number> <username>@<local ip adress>  
