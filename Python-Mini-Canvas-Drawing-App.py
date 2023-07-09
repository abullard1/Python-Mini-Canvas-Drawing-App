# Imports
import tkinter
from enum import Enum
from PIL import ImageGrab
from tkinter import filedialog

# Global variables
global canvas, click_counter, clickCoordsArrayDict, draw_mode, currently_selected_item, polygon_dict, line_dict, \
    polygon_rect_dict, line_rect_dict, control_points_hidden, middle_mouse_down, bezier_rect_dict, bezier_dict, color_var, root

# Constants
RECT_SIZE = 5  # Size of the control point rectangles
RECT_COLOR = "white"  # Color of the control point rectangles
BEZIER_SEGMENTS = 100  # Line segments to approximate the Bezier curve
ZOOM_FACTOR = 1.1  # Zoom factor for the mouse wheel


def tkinter_setup():
    global canvas, color_var, root

    # Initialize global variables (probably should have used classes from the get go)
    init_draw_mode()
    init_click_counter()
    init_click_coords_array_dict()
    init_line_dict()
    init_polygon_dict()
    init_polygon_rect_dict()
    init_line_rect_dict()
    init_currently_selected_item()
    init_control_points_hidden()
    init_middle_mouse_down()
    init_bezier_dict()
    init_bezier_rect_dict()

    # Initialize tkinter
    root = tkinter.Tk()
    root.attributes("-fullscreen", True, "-topmost", True)
    root.configure(background="white")
    root.bind("<Escape>", lambda e: root.destroy())
    root.title("Studienleistung 2")
    root.geometry("1920x1080")
    root.resizable(False, False)

    # Initialize the color dropdown menu
    color_var = tkinter.StringVar(root)
    color_var.set("white")  # default value
    color_options = ["white", "red", "green", "blue", "yellow", "purple", "orange", "black"]
    color_menu = tkinter.OptionMenu(root, color_var, *color_options)
    color_menu.pack(side="left", anchor="ne", expand=True, padx=10, pady=10)

    # Initialize the save button
    save_button = tkinter.Button(root, text="Save Image", command=save_image)
    save_button.pack(side="left", anchor="ne", expand=True, padx=10, pady=10)

    # Initialize the mode buttons
    mode_button_frame = tkinter.Frame(root)
    mode_button_frame.pack(side="left", anchor="ne", expand=True, padx=10, pady=10)

    # Line, Polygon, Bezier buttons
    line_button = tkinter.Button(mode_button_frame, text="Line", command=lambda: set_line_mode(), width=10, height=2)
    line_button.pack()
    polygon_button = tkinter.Button(mode_button_frame, text="Polygon", command=lambda: set_polygon_mode(), width=10,
                                    height=2)
    polygon_button.pack()
    bezier_curve_button = tkinter.Button(mode_button_frame, text="Bezier", command=lambda: set_bezier_mode(), width=10,
                                         height=2)
    bezier_curve_button.pack()

    # Apply button
    apply_button_frame = tkinter.Frame(root)
    apply_button_frame.pack(side="left", anchor="n", expand=False, padx=10, pady=10)

    # Select button
    select_button = tkinter.Button(apply_button_frame, width=10, height=2, text="Select",
                                   command=lambda: set_select_mode())
    select_button.pack()

    # Apply button
    apply_button = tkinter.Button(apply_button_frame, text="Apply", command=lambda: create_poly(), width=10, height=2)
    apply_button.pack()

    # Close button
    close_button_frame = tkinter.Frame(root)
    close_button_frame.pack(side="right", anchor="nw", expand=True, padx=10, pady=10)
    close_button = tkinter.Button(close_button_frame, text="Close", command=root.destroy, width=10, height=2)
    close_button.pack()

    # Canvas setup
    frame = tkinter.Frame(root, width=1920, height=1080, background="white")
    frame.pack(fill="both", expand=True)
    canvas = tkinter.Canvas(frame, width=1800, height=1000, background="black", highlightthickness=10,
                            highlightbackground="grey")

    # Mouse/Key Bindings
    canvas.bind("<Button-1>", left_click_callback)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<Button-2>", middle_click_callback)
    canvas.bind("<ButtonRelease-2>", middle_release_callback)
    canvas.bind("<MouseWheel>", zoom)
    root.bind("<KeyPress>", keypress)

    canvas.pack(expand=False, side="bottom", anchor="center", padx=10, pady=10)

    root.mainloop()


# Callback for the left mouse button
def left_click_callback(event):
    global click_counter, clickCoordsArrayDict, currently_selected_item, line_dict, polygon_rect_dict, line_rect_dict

    ### Line mode ###
    # Click counter used to track the number of clicks already made
    click_counter += 1
    if draw_mode == Mode.LINE:
        if click_counter == 1:
            clickCoordsArrayDict[0] = [event.x, event.y]
            # Create the rectangle for the first control point
            line_rect_dict[len(line_dict)] = create_rect(clickCoordsArrayDict[0][0], clickCoordsArrayDict[0][1],
                                                         str(len(line_dict)) + "," + str(0))

        if click_counter == 2:
            clickCoordsArrayDict[1] = [event.x, event.y]
            # Create the rectangle for the second control point
            line_rect_dict[len(line_dict)] = [line_rect_dict[len(line_rect_dict) - 1],
                                              create_rect(clickCoordsArrayDict[1][0], clickCoordsArrayDict[1][1],
                                                          str(len(line_dict)) + "," + str(1))]
            # Create the line
            line_dict[len(line_dict)] = draw_line(clickCoordsArrayDict[0][0], clickCoordsArrayDict[0][1],
                                                  clickCoordsArrayDict[1][0], clickCoordsArrayDict[1][1],
                                                  len(line_dict))

            # Reset the click counter
            click_counter = 0

    ### Polygon mode ###
    if draw_mode == Mode.POLYGON:
        # Create the rectangle for the control point
        rect = create_rect(event.x, event.y, str(len(polygon_dict)) + "," + str(click_counter - 1))
        if len(polygon_dict) not in polygon_rect_dict:
            polygon_rect_dict[len(polygon_dict)] = []
        polygon_rect_dict[len(polygon_dict)].append(rect)
        clickCoordsArrayDict[click_counter - 1] = [event.x, event.y]

    ### Bezier mode ###
    if draw_mode == Mode.BEZIER:
        # Create the rectangle for the control point
        if click_counter == 1:
            clickCoordsArrayDict[0] = [event.x, event.y]
            bezier_rect_dict[len(bezier_dict)] = [create_rect(clickCoordsArrayDict[0][0], clickCoordsArrayDict[0][1],
                                                              str(len(bezier_dict)) + "," + str(0))]
            print(bezier_rect_dict, bezier_dict)

        # Create the rectangle for the second control point
        elif click_counter == 2:
            clickCoordsArrayDict[1] = [event.x, event.y]
            bezier_rect_dict[len(bezier_dict)].append(
                create_rect(clickCoordsArrayDict[1][0], clickCoordsArrayDict[1][1],
                            str(len(bezier_dict)) + "," + str(1)))

        # Create the rectangle for the third control point
        elif click_counter == 3:
            clickCoordsArrayDict[2] = [event.x, event.y]
            bezier_rect_dict[len(bezier_dict)].append(
                create_rect(clickCoordsArrayDict[2][0], clickCoordsArrayDict[2][1],
                            str(len(bezier_dict)) + "," + str(2)))

            # Creates the Bezier curve
            bezier_dict[len(bezier_dict)] = draw_bezier(clickCoordsArrayDict[0][0], clickCoordsArrayDict[0][1],
                                                        clickCoordsArrayDict[1][0], clickCoordsArrayDict[1][1],
                                                        clickCoordsArrayDict[2][0], clickCoordsArrayDict[2][1],
                                                        len(bezier_dict))
            print(bezier_rect_dict, bezier_dict)
            click_counter = 0

    ### Select mode ###
    if draw_mode == Mode.SELECT:
        currently_selected_item = canvas.find_closest(event.x, event.y)


# Callback for the when the mouse is dragged
def on_drag(event):
    global currently_selected_item, middle_mouse_down

    # Checks if the middle mouse button is down for when the user is dragging the canvas
    if not middle_mouse_down:
        # Gets the item type of the currently selected item
        item_type = canvas.type(currently_selected_item)

        # Checks if the currently selected item is a rectangle/control point
        if item_type == "rectangle":
            canvas.coords(currently_selected_item, event.x - 3, event.y - 3, event.x + 3, event.y + 3)

            # Extracts the index info from the tag of the rectangle (to which shape does it belong to and what
            # index does the rectangle have within the shape)
            rect_tag = str(canvas.gettags(currently_selected_item)[0]).split(",")[0].strip("(").strip("\'")
            rect_index = int(str(canvas.gettags(currently_selected_item)[0]).split(",")[1].strip(")").strip("\'"))

            # Checks if the currently selected item is a control point of a line
            for (i, line) in line_dict.items():
                if rect_tag == str(i):
                    # Gets the coordinates of the other control point of the line
                    other_rect_coords = list(canvas.coords(line_rect_dict[i][1 - rect_index]))

                    # Creates the new coordinates for the line based on the event coordinates and the coordinates
                    if rect_index == 0:
                        new_line_coords = [event.x, event.y, other_rect_coords[0] + 3, other_rect_coords[1] + 3]
                    else:
                        new_line_coords = [other_rect_coords[0] + 3, other_rect_coords[1] + 3, event.x, event.y]

                    # Deletes the old line and create a new one with the new coordinates
                    canvas.delete(line)
                    line_dict[i] = canvas.create_line(*new_line_coords, fill=color_var.get(), width=2, tag=rect_tag)

                    break

            # Checks if the currently selected item is a control point of a polygon
            for (i, polygon) in polygon_dict.items():
                if rect_tag == str(i):
                    # Gets the coordinates of the other control points of the polygon
                    other_rect_coords = []
                    for index, rect in enumerate(polygon_rect_dict[i]):
                        if index != rect_index:
                            other_rect_coords.append(list(canvas.coords(rect)))

                    # Inserts the new coordinates for dragged rectangle
                    other_rect_coords.insert(rect_index, [event.x, event.y])

                    # Flattens list of coordinates
                    new_polygon_coords = [coord for sublist in other_rect_coords for coord in sublist]

                    # Deletes the old polygon and create a new one with the new coordinates
                    canvas.delete(polygon)
                    polygon_dict[i] = canvas.create_polygon(*new_polygon_coords, fill=color_var.get())

                    break

            # Checks if the currently selected item is a control point of a Bezier curve
            for (i, bezier_lines) in bezier_dict.items():
                if rect_tag == str(i):
                    # Gets the coordinates of the other control points
                    other_rect_coords = []
                    for index, rect in enumerate(bezier_rect_dict[i]):
                        if index != rect_index:
                            other_rect_coords.append(list(canvas.coords(rect)))

                    # Inserts the new coordinates for dragged rectangle
                    other_rect_coords.insert(rect_index, [event.x, event.y])

                    # Deletes the old Bezier curve
                    for bezier_line in bezier_lines:
                        canvas.delete(bezier_line)

                    # Draws the new Bezier curve
                    bezier_dict[i] = draw_bezier(other_rect_coords[0][0], other_rect_coords[0][1],
                                                 other_rect_coords[1][0], other_rect_coords[1][1],
                                                 other_rect_coords[2][0], other_rect_coords[2][1],
                                                 i)

                    break


# Callback for when the middle mouse button is pressed
def middle_click_callback(event):
    global middle_mouse_down
    middle_mouse_down = True
    move_all(event.x, event.y)


# Callback for when the middle mouse button is released
def middle_release_callback(event):
    global middle_mouse_down
    middle_mouse_down = False


# Callback for when the mouse wheel is scrolled
def keypress(event):
    if event.char == "x":
        if control_points_hidden:
            show_control_points()
        else:
            hide_control_points()
    if event.char == "c":
        clear_canvas()


# Creates a rectangle at the given coordinates and returns the rectangle object (used for control points)
def create_rect(x, y, tag):
    x = x - RECT_SIZE / 2
    y = y - RECT_SIZE / 2
    return canvas.create_rectangle(x, y, x + RECT_SIZE, y + RECT_SIZE, fill=RECT_COLOR, tag=tag)


# Creates a line at the given coordinates and returns the line object
def draw_line(x1, y1, x2, y2, tag):
    return canvas.create_line(x1, y1, x2, y2, fill=color_var.get(), width=2, tag=tag)


# Creates a polygon at the given coordinates and returns the polygon object
def draw_polygon(coords, **kwargs):
    if len(coords) > 0:
        polygon_dict[len(polygon_dict)] = canvas.create_polygon(coords, **kwargs)


# Creates a Bezier curve at the given coordinates and returns the Bezier curve lines as a list
def draw_bezier(x1, y1, x2, y2, cx, cy, tag):
    bezier_lines = []
    # https://www.vectornator.io/blog/bezier-curves/#:~:text=A%20B%C3%A9zier%20curve%20can%20approximate,is%20generated%20using%20linear%20interpolations.
    for t in range(BEZIER_SEGMENTS):
        t /= BEZIER_SEGMENTS
        nx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2
        ny = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2
        if t > 0:
            bezier_lines.append(draw_line(prev_nx, prev_ny, nx, ny, tag))
        prev_nx, prev_ny = nx, ny
    return bezier_lines


# Hides all control points
def hide_control_points():
    global line_rect_dict, polygon_rect_dict, control_points_hidden
    control_points_hidden = True
    # Disable line rectangles
    for rect in line_rect_dict.values():
        for r in rect:
            canvas.itemconfigure(r, state="hidden")

    # Disable polygon rectangles
    for rect in polygon_rect_dict.values():
        for r in rect:
            canvas.itemconfigure(r, state="hidden")

    for rect in bezier_rect_dict.values():
        for r in rect:
            canvas.itemconfigure(r, state="hidden")


# Shows all control points
def show_control_points():
    global line_rect_dict, polygon_rect_dict, control_points_hidden
    control_points_hidden = False
    # Enable line rectangles
    for rect in line_rect_dict.values():
        for r in rect:
            canvas.itemconfigure(r, state="normal")

    # Enable polygon rectangles
    for rect in polygon_rect_dict.values():
        for r in rect:
            canvas.itemconfigure(r, state="normal")

    for rect in bezier_rect_dict.values():
        for r in rect:
            canvas.itemconfigure(r, state="normal")


# Zooms in or out on the canvas (Still buggy and zooms the whole window)
def zoom(event):
    global canvas
    # Respond to Linux (event.num) or Windows and Mac (event.delta) scroll wheel event
    if event.num == 4 or event.delta > 0:
        scale = ZOOM_FACTOR
    else:
        scale = 1 / ZOOM_FACTOR

    # Rescale all objects on canvas. Note that this also rescales text font sizes.
    x0, y0, x1, y1 = canvas.bbox("all")  # get bounding box of all objects
    canvas.scale("all", x0, y0, scale, scale)

    # Resize the canvas according to the new scale
    new_width = (x1 - x0) * scale
    new_height = (y1 - y0) * scale
    canvas.config(width=new_width, height=new_height)


# Sets the draw mode to the line mode
def set_line_mode():
    global draw_mode, clickCoordsArrayDict
    init_click_counter()
    draw_mode = Mode.LINE
    clickCoordsArrayDict = {}


# Sets the draw mode to the polygon mode
def set_polygon_mode():
    global draw_mode, clickCoordsArrayDict
    init_click_counter()
    draw_mode = Mode.POLYGON
    clickCoordsArrayDict = {}


# Sets the draw mode to the Bezier mode
def set_bezier_mode():
    global draw_mode, clickCoordsArrayDict
    init_click_counter()
    draw_mode = Mode.BEZIER
    clickCoordsArrayDict = {}


# Sets the draw mode to the select mode
def set_select_mode():
    global draw_mode
    init_click_counter()
    draw_mode = Mode.SELECT

# Resets the draw mode
def reset_draw_mode():
    global draw_mode
    draw_mode = Mode.NONE


# Creates a polygon from the points that the user clicked
def create_poly():
    global applyButtonClicked, clickCoordsArrayDict
    clickCoordsArrayDictList = list(clickCoordsArrayDict.values())
    draw_polygon(clickCoordsArrayDictList, fill=color_var.get())
    clickCoordsArrayDict = {}


# Clears the canvas
def clear_canvas():
    global line_dict, polygon_dict, line_rect_dict, polygon_rect_dict
    canvas.delete("all")
    init_line_dict()
    init_polygon_dict()
    init_line_rect_dict()
    init_polygon_rect_dict()


# Moves all objects on the canvas by the given amount
def move_all(dx, dy):
    for shape in canvas.find_all():
        canvas.move(shape, dx, dy)


# Saves the canvas as an image
def save_image(filename="image"):
    global root
    # Opens a file dialog and gets the directory that the user selected
    directory = filedialog.askdirectory()
    fileName = directory + "/" + filename

    # Uses the PIL libraries ImageGrab to capture the entire window
    root.update()
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    x1 = x + root.winfo_width()
    y1 = y + root.winfo_height()
    img = ImageGrab.grab().crop((x, y, x1, y1))

    # Saves the image as a PNG file
    img.save(fileName + ".png", "png")


# Global variable init methods
def init_click_counter():
    global click_counter
    click_counter = 0


def init_click_coords_array_dict():
    global clickCoordsArrayDict
    clickCoordsArrayDict = {}


def init_draw_mode():
    reset_draw_mode()


def init_polygon_dict():
    global polygon_dict
    polygon_dict = {}


def init_polygon_rect_dict():
    global polygon_rect_dict
    polygon_rect_dict = {}


def init_currently_selected_item():
    global currently_selected_item
    currently_selected_item = None


def init_line_rect_dict():
    global line_rect_dict
    line_rect_dict = {}


def init_line_dict():
    global line_dict
    line_dict = {}


def init_bezier_dict():
    global bezier_dict
    bezier_dict = {}


def init_bezier_rect_dict():
    global bezier_rect_dict
    bezier_rect_dict = {}


def init_control_points_hidden():
    global control_points_hidden
    control_points_hidden = False


def init_middle_mouse_down():
    global middle_mouse_down
    middle_mouse_down = False


# Draw Mode Enum
class Mode(Enum):
    NONE = 0
    LINE = 1
    POLYGON = 2
    BEZIER = 3
    SELECT = 4


def main():
    tkinter_setup()


if __name__ == "__main__":
    main()
