import logging
import datetime
import pyfiglet
import colorama
from pythonosc import dispatcher
from pythonosc import osc_server
from tinyoscquery.queryservice import OSCQueryService
from tinyoscquery.utility  import get_open_udp_port, get_open_tcp_port


def receiveOscParameters(dict_filter_and_target, ip_address="127.0.0.1", title="OSC LOGGER"):
    osc_port = get_open_udp_port()
    http_port = get_open_tcp_port()
    osc_dispatcher = dispatcher.Dispatcher()
    for filter, target in dict_filter_and_target.items():
        osc_dispatcher.map(filter, target)
    osc_udp_server = osc_server.ThreadingOSCUDPServer((ip_address, osc_port), osc_dispatcher)

    osc_client = OSCQueryService(title, http_port, osc_port)
    for filter, target in dict_filter_and_target.items():
        osc_client.advertise_endpoint(filter)

    osc_udp_server.serve_forever()

def main():
    colorama.init()
    logging.basicConfig(filename='osc_logger.log', level=logging.INFO, format='%(asctime)s - %(message)s')

    print(colorama.Fore.LIGHTCYAN_EX + pyfiglet.figlet_format("OSC LOGGER", font="slant"))
    print(colorama.Fore.WHITE + "=============================")
    print(colorama.Fore.GREEN + "受信したOSCデータを表示するツール")
    print(colorama.Fore.GREEN + "Ideas by: " + colorama.Fore.YELLOW + "m's software")
    print(colorama.Fore.WHITE + "Version: " + colorama.Fore.YELLOW + "1.0.0")
    print(colorama.Fore.WHITE + "Developed by: " + colorama.Fore.YELLOW + "@misya_ai")
    print(colorama.Fore.WHITE + "=============================")

    osc_parameter_prefix = "/avatar/parameters/"
    def print_handler_all(address, *args):
        print(colorama.Fore.YELLOW + f"[{datetime.datetime.now()}]", end=" ")
        print(colorama.Fore.GREEN + f"{address}", end=" ")
        print(colorama.Fore.WHITE + f"{args}")

        log_message = f"{address} {args}"
        logging.info(log_message)

    dict_filter_and_target = {
        osc_parameter_prefix + "*": print_handler_all,
    }
    receiveOscParameters(dict_filter_and_target)

if __name__ == "__main__":
    main()
