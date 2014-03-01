
import sys

from client import AntClient
from vis import Vis




def main():

	if len(sys.argv) < 2:
		sys.exit(1)

	client = AntClient(sys.argv[1], False, 'spectator^^')  ## here happens the network stuff in the AntClient ctor

	vis = Vis(client)


	while True:
		client.update_world()
		vis.update()




if __name__ == '__main__':
	main()
