
import sys

from client import AntClient
from vis import Vis




def main():

	if len(sys.argv) < 2:
		sys.exit(1)

	client = AntClient(sys.argv[1], True)  ## here happens the network stuff in the AntClient ctor

	vis = Vis(client)

	client.update_world()
	client.futtersuche_focus()

	while True:
		client.update_world()
		client.futtersuche_go()
		client.send_actions()
		client.send_action([1] * 16)
		vis.update()




if __name__ == '__main__':
	main()
