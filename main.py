import logging
import time
import threading
import pyfiglet
import colorama
from pythonosc import dispatcher
from pythonosc import osc_server
from tinyoscquery.queryservice import OSCQueryService
from tinyoscquery.utility  import get_open_udp_port, get_open_tcp_port
from rich.live import Live
from rich.table import Table
from rich import box
from rich.console import Console

colorama.init()
logging.basicConfig(filename='osc_logger.log', level=logging.INFO, format='[%(asctime)s] %(message)s')

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
    osc_udp_server.serve_forever(poll_interval=0.5)

class App:
    def __init__(self):
        self.table_data = {}

    def logger(self):
        osc_parameter_prefix = "/avatar/parameters/"
        def handler(address, *args):
            value = args[0]
            if isinstance(value, float):
                value = round(value, 8)
            self.table_data[address] = value
            logging.info(f"{address} {args[0]}")

        dict_filter_and_target = {
            osc_parameter_prefix + "*": handler,
        }
        receiveOscParameters(dict_filter_and_target)

    def generate_table(self):
        table = Table(box=box.ASCII, show_header=True, header_style="bold white")
        table.add_column("No.", justify="left", style="white")
        table.add_column("Address", justify="left", style="green")
        table.add_column("Values", justify="left", style="magenta")
        table_data_copy = self.table_data.copy()

        no = 1
        for address, value in table_data_copy.items():
            table.add_row(str(no), address, str(value))
            no += 1
        return table

    def start(self):
        while self.table_data == {}:
            time.sleep(0.1)

        with Live(self.generate_table(), refresh_per_second=30) as live:
            while True:
                live.update(self.generate_table())
                time.sleep(0.1)

if __name__ == "__main__":
    # print(colorama.Fore.WHITE + "==========================================================")
    # print(colorama.Fore.LIGHTCYAN_EX + pyfiglet.figlet_format("OSC Logger", font="slant"))
    # print(colorama.Fore.WHITE + "Ideas by: " + colorama.Fore.YELLOW + "m's software")
    # print(colorama.Fore.WHITE + "Version: " + colorama.Fore.YELLOW + "1.0.0")
    # print(colorama.Fore.WHITE + "Developed by: " + colorama.Fore.YELLOW + "@misya_ai")
    # print(colorama.Fore.WHITE + "==========================================================")

    table = Table(box=box.HORIZONTALS, show_header=True, header_style="bold cyan")
    table.add_column(pyfiglet.figlet_format("OSC Logger", font="slant"), justify="left")
    table.add_row("Ideas by: m's software", style="yellow")
    table.add_row("Version: 1.0.0", style="yellow")
    table.add_row("Developed by: @misya_ai", style="yellow")
    console = Console()
    console.print(table)

    app = App()
    th_receive = threading.Thread(target=app.logger)
    th_receive.daemon = True
    th_receive.start()
    app.start()
