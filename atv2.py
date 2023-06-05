import datetime
import optparse
import browsercookie
import termcolor
import os

def get_chrome_datetime(chromedate):
    if chromedate != 86400000000 and chromedate:
        try:
            return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=chromedate)
        except Exception as e:
            print(f"Error: {e}, chromedate: {chromedate}")
            return chromedate
    else:
        return ""

def list_all_cookies(browserCookie):
    output_folder = 'all_cookies'
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    output_file = f"{output_folder}/cookies.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        for cookie in browserCookie:
            f.write(f'Host: {cookie.domain}\n')
            f.write(f'Cookie name (session): {cookie.name}\n')
            f.write(f'Cookie value: {cookie.value}\n')
            f.write(f'Expires datetime (UTC): {get_chrome_datetime(cookie.expires)}')
            f.write("\n===============================================================\n")
            
def search_cookies_host(host, browserCookie):
    verifica = False
    
    output_folder = host.replace('.', '_') + '_cookies'
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for cookie in browserCookie:
        if host in cookie.domain:
            verifica = True
            output_file = f"{output_folder}/{cookie.name}Cookies.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f'Host: {cookie.domain}\n')
                f.write(f'Cookie name (session): {cookie.name}\n')
                f.write(f'Cookie value: {cookie.value}\n')
                f.write(f'Expires datetime (UTC): {get_chrome_datetime(cookie.expires)}')
    
    if verifica is False:
        os.removedirs(output_folder)
    return verifica
                
def main():
    browserCookie = browsercookie.load()
        
    while True:
        print(termcolor.colored(f"[*] Escolha uma das opções", 'cyan'))
        print(termcolor.colored(f"[0] Sair", 'cyan'))
        print(termcolor.colored(f"[1] Listar todos os cookies", 'cyan'))
        print(termcolor.colored(f"[2] Pesquisar pelo em específico", 'cyan'))
            
        op = input(termcolor.colored(">", "white"))
            
        if op == '0':
                print(termcolor.colored("[-] Finalizando...", 'magenta'))
                return;
        if op == '1':
                list_all_cookies(browserCookie)
                print(termcolor.colored(f"[+] Cookies listados", 'green'))
        if op == '2':
                
            host = input(termcolor.colored("Host: ", "white"))
                    
            if search_cookies_host(host, browserCookie) is False:
                    print(termcolor.colored(f"[-] Não foi encontrado cookies para o host [{host}]", 'red'))
            else:
                print(termcolor.colored(f"[+] Cookies encontrados para o host [{host}]", 'green'))
if __name__ == "__main__":
    main()