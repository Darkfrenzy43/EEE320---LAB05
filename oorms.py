"""

    Description:

    Provides the user interface for the Object-oriented Restaurant Management
    application (OORMS). This includes the server's view and a window simulating
    the tape of a bill printer.

    Notes:
        - None for now


    Status:
        - Velasco (November 4, 2022) COMPLETED: Reading code for first time and commenting as needed
        - Velasco (November 4, 2022): Beginning rough implementation of planned Payment UI
            - Create the UI
                - Velasco: Re-sizing of the canvas window was found (use canvas.config(...))
                - Delete: Fuck around playing with the available tkinter shit. Create buttons, print shit, etc.
                - Velasco: Creating EXIT button that returns UI to table view
                - Mohammed: Creating the button layout


            - Create the controller
            - Create the model? <-- Is this needed



    Submitting lab group: OCdt Al-Ansar Mohammed, OCdt Velasco
    Submission date: November 24th, 2022

    Original code by EEE320 instructors.
"""

# --- Importing Libraries and Modules ---

import math
import tkinter as tk
from abc import ABC

from constants import *
from controller import RestaurantController
from model import Restaurant


# --- Defining Classes ---

class RestaurantView(tk.Frame, ABC):
    """  An abstract superclass for the views in the system. """



    def __init__(self, master, restaurant, window_width, window_height, controller_class):
        """ Constructor to RestaurantView class. """

        # Saving master arg as attribute
        self.master = master;


        super().__init__(master)
        self.grid()
        self.canvas = tk.Canvas(self, width=window_width, height=window_height,
                                borderwidth=0, highlightthickness=0)
        self.canvas.grid()
        self.canvas.update()
        self.restaurant = restaurant
        self.restaurant.add_view(self)
        self.controller = controller_class(self, restaurant)
        self.controller.create_ui()


    def make_button(self, text, action, size=BUTTON_SIZE, location=BUTTON_BOTTOM_RIGHT,
                    rect_style=BUTTON_STYLE, text_style=BUTTON_TEXT_STYLE):
        """ Provided method that handles button creation in the views. """

        w, h = size
        x0, y0 = location
        box = self.canvas.create_rectangle(x0, y0, x0 + w, y0 + h, **rect_style)
        label = self.canvas.create_text(x0 + w / 2, y0 + h / 2, text=text, **text_style)
        self.canvas.tag_bind(box, '<Button-1>', action)
        self.canvas.tag_bind(label, '<Button-1>', action)


    def update(self):
        """ Method calls current controller's create_ui() method which tells this view re-draw the user interface. """
        self.controller.create_ui()

    def set_controller(self, controller):
        """ Method switches current controller object to <controller> object passed through args. """
        self.controller = controller


class ServerView(RestaurantView):
    """ Inherits RestaurantView class.

    This view appears on the left window when the system is run. View contains the entire view of the restaurant -
    including the tables and chairs in it - and when pressed, shows the order views of the associated tables and chairs.
    Same view found in Lab 3. """

    # Boolean for the Payment UI button
    fuck_button_pressed = False;

    def __init__(self, master, restaurant, printer_window):
        """ Constructor to ServerView. """

        # Calling superclass constructor
        super().__init__(master, restaurant, SERVER_VIEW_WIDTH, SERVER_VIEW_HEIGHT, RestaurantController)

        # Initializing the printer window
        self.printer_window = printer_window


    def create_restaurant_ui(self):
        """ This method gets called in the RestaurantController object.

        When called, uses tkinter's provided canvas methods to create the restaurant's user interface.
        More specifically, it calls the methods that draws out the tables, and defines the function handler
        in the event a table is touched. """

        self.canvas.delete(tk.ALL)
        view_ids = []
        for ix, table in enumerate(self.restaurant.tables):
            table_id, seat_ids = self.draw_table(table, scale=RESTAURANT_SCALE)
            view_ids.append((table_id, seat_ids))
        for ix, (table_id, seat_ids) in enumerate(view_ids):
            # §54.7 "extra arguments trick" in Tkinter 8.5 reference by Shipman
            # Used to capture current value of ix as table_index for use when
            # handler is called (i.e., when screen is clicked).
            def table_touch_handler(_, table_number=ix):
                self.controller.table_touched(table_number)

            self.canvas.tag_bind(table_id, '<Button-1>', table_touch_handler)
            for seat_id in seat_ids:
                self.canvas.tag_bind(seat_id, '<Button-1>', table_touch_handler)


    def create_table_ui(self, table):
        """ This method Is called within the TableController object.

        The Table object that was selected is the <table> passed through the argument.

        When a specific table/chair is clicked, method uses provided tkinter methods to create the clicked upon table's
        user interface by drawing it and its selected chairs onto the canvas, and defines the handler for when a given
        seat is clicked on. """

        # Configuring size of window here to be designed size - doesn't do anything if already of that size
        self.canvas.config(width=SERVER_VIEW_WIDTH, height=SERVER_VIEW_HEIGHT);

        self.canvas.delete(tk.ALL)
        table_id, seat_ids = self.draw_table(table, location=SINGLE_TABLE_LOCATION)
        for ix, seat_id in enumerate(seat_ids):
            def handler(_, seat_number=ix):
                self.controller.seat_touched(seat_number)

            self.canvas.tag_bind(seat_id, '<Button-1>', handler)
        self.make_button('Done', action=lambda event: self.controller.done())
        if table.has_any_active_orders():

            # This button opens up the Payment UI
            self.make_button('Create Bills', 
                action=lambda event: self.controller.make_bills(self.printer_window),
                location=BUTTON_BOTTOM_LEFT)



    def draw_table(self, table, location=None, scale=1):
        """ Uses Tkinter's provided canvas methods to draw a given table object out onto the canvas.

        <table> is the table object to be drawn, <location, defaulted to None> refers to where the table object
        is to be drawn on the canvas, and <scale, defaulted to 1> is how large the table is to be drawn.

        Returns the IDs of the table and seats created by tkinter for event binding with the handlers."""

        offset_x0, offset_y0 = location if location else table.location
        seats_per_side = math.ceil(table.n_seats / 2)
        table_height = SEAT_DIAM * seats_per_side + SEAT_SPACING * (seats_per_side - 1)
        table_x0 = SEAT_DIAM + SEAT_SPACING
        table_bbox = scale_and_offset(table_x0, 0, TABLE_WIDTH, table_height,
                                      offset_x0, offset_y0, scale)
        table_id = self.canvas.create_rectangle(*table_bbox, **TABLE_STYLE)
        far_seat_x0 = table_x0 + TABLE_WIDTH + SEAT_SPACING
        seat_ids = []
        for ix in range(table.n_seats):
            seat_x0 = (ix % 2) * far_seat_x0
            seat_y0 = (ix // 2 * (SEAT_DIAM + SEAT_SPACING) +
                       (table.n_seats % 2) * (ix % 2) * (SEAT_DIAM + SEAT_SPACING) / 2)
            seat_bbox = scale_and_offset(seat_x0, seat_y0, SEAT_DIAM, SEAT_DIAM,
                                         offset_x0, offset_y0, scale)
            style = FULL_SEAT_STYLE if table.has_order_for(ix) else EMPTY_SEAT_STYLE
            seat_id = self.canvas.create_oval(*seat_bbox, **style)
            seat_ids.append(seat_id)
        return table_id, seat_ids

    def create_order_ui(self, order):
        """ This method is called within the OrderController object.

        Uses tkinter's provided methods to create the user interface of the order menu
        when a given seat object is selected from the table user interface.

        <order> is the order object that is to track all the orders made for the selected seat. """



        self.canvas.delete(tk.ALL)
        for ix, item in enumerate(self.restaurant.menu_items):
            w, h, margin = MENU_ITEM_SIZE
            x0 = margin
            y0 = margin + (h + margin) * ix

            def handler(_, menuitem=item):
                self.controller.add_item(menuitem)

            self.make_button(item.name, handler, (w, h), (x0, y0))
        self.draw_order(order)
        self.make_button('Cancel', lambda event: self.controller.cancel_changes(), location=BUTTON_BOTTOM_LEFT)
        self.make_button('Update Order', lambda event: self.controller.update_order())


    def draw_order(self, order):
        """ Draws out the orders placed after pressing a menu item button.  """

        x0, h, m = ORDER_ITEM_LOCATION
        for ix, item in enumerate(order.items):
            y0 = m + ix * h
            self.canvas.create_text(x0, y0, text=item.details.name,
                                    anchor=tk.NW)
            dot_style = ORDERED_STYLE if item.has_been_ordered() else NOT_YET_ORDERED_STYLE
            self.canvas.create_oval(x0 - DOT_SIZE - DOT_MARGIN, y0, x0 - DOT_MARGIN, y0 + DOT_SIZE, **dot_style)
            if item.can_be_cancelled():

                def handler(_, cancelled_item=item):
                    self.controller.remove(cancelled_item)

                self.make_button('X', handler, size=CANCEL_SIZE, rect_style=CANCEL_STYLE,
                                 location=(x0 - 2*(DOT_SIZE + DOT_MARGIN), y0))
        self.canvas.create_text(x0, m + len(order.items) * h,
                                text=f'Total: {order.total_cost():.2f}',
                                anchor=tk.NW)




    # ----- Adding some of my own shit here let's do this
    def create_payment_ui(self):
        """ This shit creates the payment ui that we have in our UI concept design idk. """

        this_width = PAYMENT_VIEW_WIDTH;
        this_height = PAYMENT_VIEW_HEIGHT;

        # Resize the canvas to payment UI dimensions, and clear canvas
        self.canvas.config(width = this_width, height = this_height);
        self.canvas.delete(tk.ALL);


        # Let's try creating some buttons and stuff (fuck around i guess)
        self.canvas.create_text(this_width/2, this_height/2, text = "I fucking love coding.", anchor = tk.CENTER);
        self.make_button('Click me. Do it.', lambda event: self.controller.fuck_around_button_pressed(), location =
            (this_width/2 - 50, this_height/2 + 20));

        # Create an exit button that returns back to table view
        self.make_button('EXIT', lambda event: self.controller.exit_pressed(), location = (10, this_height - 40));

        # Playing with interface buttons
        if self.fuck_button_pressed is True:

            self.canvas.create_text(this_width / 2, this_height / 2 + 100,
                                    text = "\"Velasco, what are you saying? I've literally never said that though.\" "
                                           "\n-Eric Cho (based)", anchor = tk.CENTER);



class Printer(tk.Frame):
    """ Simulates a physical printer with a monospaced font, a maximum of 40 characters wide.

    To print, call the print() method passing the desired text as a parameter.
    The text may include \n (newline) characters to indicate line breaks.
    """

    def __init__(self, master):
        """ Constructor of the Printer object. """

        # Initialize a bunch of stuff here idk. (lol yee love these comments)
        super().__init__(master)
        self.grid()
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.tape = tk.Text(self, wrap=None, bd=0, yscrollcommand=scrollbar.set,
                            font=TAPE_FONT, state=tk.DISABLED,
                            width=TAPE_WIDTH, height=VISIBLE_LINES)
        self.tape.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        scrollbar.config(command=self.tape.yview)

    def print(self, text):
        """ Prints a bill object. """

        # This stuff we changing ?
        self.tape['state'] = tk.NORMAL
        self.tape.insert(tk.END, text)
        self.tape.insert(tk.END, '\n')
        self.tape['state'] = tk.DISABLED
        self.tape.see(tk.END)



# --- Defining Separate Functions ---

def scale_and_offset(x0, y0, width, height, offset_x0, offset_y0, scale):
    return ((offset_x0 + x0) * scale,
            (offset_y0 + y0) * scale,
            (offset_x0 + x0 + width) * scale,
            (offset_y0 + y0 + height) * scale)



# --- Entry Point ---

if __name__ == "__main__":

    # root is the window
    root = tk.Tk()

    printer_window = tk.Toplevel()
    printer_proxy = Printer(printer_window)
    printer_window.title('Printer Tape')
    printer_window.wm_resizable(0, 0)

    restaurant_info = Restaurant()
    ServerView(root, restaurant_info, printer_proxy)
    root.title('Server View v2')
    root.wm_resizable(0, 0)

    # nicely align the two windows
    root.update_idletasks()
    ph = printer_window.winfo_height()
    pw = printer_window.winfo_width()
    sw = root.winfo_width()
    sx = root.winfo_x()
    sy = root.winfo_y()
    printer_window.geometry(f'{pw}x{ph}+{sx+sw+10}+{sy}')

    root.mainloop()
