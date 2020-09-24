import pygame
import math
from queue import PriorityQueue

WIDTH = 500
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):  return self.row, self.col

	def is_closed(self):  return self.color == RED
	def is_open(self):  return self.color == GREEN
	def is_barrier(self):  return self.color == BLACK
	def is_start(self):  return self.color == ORANGE
	def is_end(self):  return self.color == TURQUOISE

	def reset(self):  self.color = WHITE

	def make_start(self):  self.color = ORANGE
	def make_closed(self):  self.color = RED
	def make_open(self):  self.color = GREEN
	def make_barrier(self):  self.color = BLACK
	def make_end(self):  self.color = TURQUOISE
	def make_path(self):  self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False


def get_abs_coords(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def A_star_algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {node: float("inf") for row in grid for node in row}
	g_score[start] = 0
	f_score = {node: float("inf") for row in grid for node in row}
	f_score[start] = get_abs_coords(start.get_pos(), end.get_pos())

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + get_abs_coords(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False


def make_grid(FIRST_ROW, width):
	grid = []
	node_width = width // FIRST_ROW
	for i in range(FIRST_ROW):
		grid.append([])
		for j in range(FIRST_ROW):
			node = Node(i, j, node_width, FIRST_ROW)
			grid[i].append(node)

	return grid


def draw_grid(win, FIRST_ROW, width):
	node_width = width // FIRST_ROW
	for r in range(FIRST_ROW):
		pygame.draw.line(win, GREY, (0, r * node_width), (width, r * node_width))
	for c in range(FIRST_ROW):
		pygame.draw.line(win, GREY, (c * node_width, 0), (c * node_width, width))


def draw(win, grid, FIRST_ROW, width):
	win.fill(WHITE)

	for row in grid:
		for node in row:
			node.draw(win)

	draw_grid(win, FIRST_ROW, width)
	pygame.display.update()


def get_clicked_pos(pos, FIRST_ROW, width):
	node_width = width // FIRST_ROW
	y, x = pos

	row = y // node_width
	col = x // node_width

	return row, col


def main(win, width):
	FIRST_ROW = 50
	grid = make_grid(FIRST_ROW, width)

	start = None
	end = None

	run = True
	while run:
		draw(win, grid, FIRST_ROW, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]: # LEFT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, FIRST_ROW, width)
				node = grid[row][col]
				if not start and node != end:
					start = node
					start.make_start()

				elif not end and node != start:
					end = node
					end.make_end()

				elif node != end and node != start:
					node.make_barrier()

			elif pygame.mouse.get_pressed()[2]: # RIGHT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, FIRST_ROW, width)
				node = grid[row][col]
				node.reset()
				if node == start:
					start = None
				elif node == end:
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					for row in grid:
						for node in row:
							node.update_neighbors(grid)

					A_star_algorithm(lambda: draw(win, grid, FIRST_ROW, width), grid, start, end)

				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(FIRST_ROW, width)

	pygame.quit()

main(WIN, WIDTH)