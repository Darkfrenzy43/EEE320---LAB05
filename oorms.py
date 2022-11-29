"""

    Description:

    Provides the user interface for the Object-oriented Restaurant Management
    application (OORMS). This includes the server's view and a window simulating
    the tape of a bill printer.

    Notes:

        1 - The term "seat orders" is used often as a dummy variable name for the Order objects within the Payment
        UI and the Bill UI. The reason why this name was used for the object was to be explicitly clear that the
        object being handled under the variable "seat order" is the order which is associated with a seat at a
        given table.

        2 - A few attributes in the model.py have been switched to private attributes in order to practice good
        encapsulation. This includes the .items list of the Order object, etc.
        
        3 - Just noting for myself the codes of the colors in Tkinter:
                
                # #fff -> white
                #999 -> Gray
                #000 -> Black
                #900 -> Dark Red
                #f00 -> Red
                #990 -> Dark Yellow
                #0f0 -> Bright Green
                #090 -> Green
                #00f -> Bright Blue
                
        4 - Made the design choice to configure the size of the ServerView Window when enter Payment UI and Bill UI.
        This is done to make space for the buttons and all.

        Accordingly, Since I don't want to have the printer window be fully covered when the Payment or Bill UI get
        accessed, I changed the distance of separation between the printer window and the ServerView window upon
        initialization of the program.

        5 - An intentional design choice of the Payment UI was that there must always be a maximum bill number of as
        many  seats at the table who have orders with OrderItems added in them. If the user trys to this,
        then the program throws an error.


    Status:
        - Velasco (November 4, 2022) COMPLETED: Reading code for first time and commenting as needed
        - Velasco (November 4, 2022): Beginning rough implementation of planned Payment UI
            - Create the UI
                - Velasco COMPLETED: Re-sizing of the canvas window was found (use canvas.config(...))
                - Velasco COMPLETED: Creating EXIT button that returns UI to table view
                - Mohammed: Creating the button layout
            - Create the controller
                - Velasco and Mohammed COMPLETED: Created as needed
            - Create the model
                - Velasco COMPLETED: Creating the bill object
            - ...
            - Velasco: It's all completed. I'll miss you Mohammed. Thanks for the help man.


    To do list:
        - Hand in.


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
from model import Restaurant;


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

        # Configuring size of window back to the original ServerView size - doesn't do anything if already of that size
        self.canvas.config(width=SERVER_VIEW_WIDTH, height=SERVER_VIEW_HEIGHT);

        self.canvas.delete(tk.ALL)
        table_id, seat_ids = self.draw_table(table, location=SINGLE_TABLE_LOCATION)
        for ix, seat_id in enumerate(seat_ids):
            def handler(_, seat_number=ix):
                self.controller.seat_touched(seat_number)

            self.canvas.tag_bind(seat_id, '<Button-1>', handler)
        self.make_button('Done', action=lambda event: self.controller.done())
        if table.has_any_active_orders():

            # This button opens up the Payment UI for the current table
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
        for ix, item in enumerate(order.get_items()):
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
        self.canvas.create_text(x0, m + len(order.get_items()) * h,
                                text=f'Total: {order.total_cost():.2f}',
                                anchor=tk.NW)


    # ----- ADDED CODE -------

    def create_payment_ui(self, table):
        """ Method draws out the Payment UI of a given table object passed through the arguments.

        <table : Table> : the table whose Payment UI is to be drawn. """

        # Retrieving UI window size from constants.
        this_width = PAYMENT_VIEW_WIDTH;
        this_height = PAYMENT_VIEW_HEIGHT;

        # Resize the canvas to payment UI dimensions and clear canvas
        self.canvas.config(width = this_width, height = this_height);
        self.canvas.delete(tk.ALL);

        # Draw button that returns back to the table view.
        self.make_button('EXIT', lambda event: self.controller.exit_pressed(), location=(20, this_height - 40));

        # Draw button that adds a bill object to the view.
        self.make_button('Add New Bill', lambda event: self.controller.add_bill_pressed(), location =
        (195, this_height - 40));

        # Draw button that automatically adds each seat in the UI to its own bill object
        self.make_button('Each Own Bill', lambda event: self.controller.each_own_bill_pressed(), location =
        (370, this_height - 40));

        # Draw button that automatically creates a bill for everyone to be in
        self.make_button('All One Bill', lambda event: self.controller.all_one_bill_pressed(), location =
        (545, this_height - 40));

        # Draw button that prints the paid bills?
        self.make_button('Print and Pay Bills', lambda event: self.controller.print_paid_bills_pressed(), location =
        (720, this_height - 40));


        # Extracting the table's orders associated with each seat, and the already created bill objects.
        seat_orders = table.return_orders();
        bill_objects = table.return_bills();

        # Drawing the seats and their info onto the canvas.
        for this_order in seat_orders:
            draw_seat_info(self.canvas, this_order, (50, 20), (5, 25), 105, 15);

        # Draw all the bills and their respective buttons onto canvas.
        for this_bill_object in bill_objects:

            # Creating handler for when a given bill object's button gets touched.
            # When one is pressed, will open the UI of said bill object.
            def this_handler(_, this_bill = this_bill_object):
                self.controller.bill_object_pressed(this_bill);

            # Draw the bill object with its function.
            draw_bill_info_button(self.canvas, this_bill_object, table, (200, 200), 150, this_handler)



    # Creating the Bill UI now
    def create_bill_ui(self, bill_obj):
        """ Method creates the bill UI of the bill object passed through the arguments.

        <bill_obj : Bill> : The bill object whose UI is being drawn. """

        # Extracting window info from the constants
        this_height = BILL_VIEW_HEIGHT;
        this_width = BILL_VIEW_WIDTH;
        self.canvas.config(width = this_width, height = this_height);

        # Delete everything on the canvas.
        self.canvas.delete(tk.ALL);


        # Drawing divider
        self.canvas.create_line(700, 0, 700, this_height, width = 2);

        # Drawing PAID status
        if bill_obj.is_paid():
            self.canvas.create_text(350, 150, text = f'PAID', anchor = tk.CENTER, font = ('Times', 30), fill = '#090');

        # Drawing window titles
        self.canvas.create_text(350, 70, text = f'Bill #{bill_obj.ID}', anchor = tk.CENTER,
                                font = ('Times', 25, 'underline'));
        self.canvas.create_text(950, 30, text = 'Unassigned Seats', anchor = tk.CENTER,
                                font = ('Times', 18, 'underline'));

        # Draw the seat orders added to this bill object (they will be sorted!)
        self.canvas.create_text(150, 205, text = f'Added Seats', anchor = tk.CENTER, font = ('Times', 18, 'underline'));
        added_orders = [str(order.get_seat_number()) for order in bill_obj.added_orders];
        added_orders.sort();
        self.canvas.create_text(150, 230, text = ', '.join(added_orders), anchor = tk.CENTER, font = ('Times', 16));

        # Draw total price of added seat orders
        total_price = 0;
        for this_order in bill_obj.added_orders:
            total_price += this_order.total_cost();
        self.canvas.create_text(550, 205, text = "Total Price", anchor = tk.CENTER, font = ('Times', 18, 'underline'));
        self.canvas.create_text(550, 230, text = '$%.2f' % total_price, anchor = tk.CENTER, font = ('Times', 18));

        # Draw unassigned orders and their buttons in the right window
        unassigned_list = bill_obj.table.return_unassigned_orders();
        for unass_seat_order in unassigned_list:

            # Handler that adds an unassigned seat to the current bill when
            # its green plus button is pressed.
            def seat_handler(_, this_seat = unass_seat_order):
                self.controller.add_order_pressed(this_seat);

            # Drawing the plus button of the unassigned seat
            draw_unassigned_seat_button(self.canvas, unass_seat_order, (775, 75), 110, 15, seat_handler,
                                        unassigned_list.index(unass_seat_order));

        # Draw the PAY, EXIT, and DELETE button for the bill UI.
        # self.make_button('PAY', lambda event: self.controller.pay_bill(), location = (590, this_height - 40));
        self.make_button('EXIT', lambda event: self.controller.exit_pressed(), location = (10, this_height - 40));
        self.make_button('DELETE', lambda event: self.controller.delete_bill(), location = (350, this_height - 40));






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


    def print_paid_bills(self, bill_list):
        """ Prints the list of paid bills with the table. """

        self.tape['state'] = tk.NORMAL

        # Opening print lines
        self.tape.insert(tk.END, '\n\n\n');
        self.tape.insert(tk.END, ">" * 13);
        self.tape.insert(tk.END, " New Payment ");
        self.tape.insert(tk.END, "<" * 13);

        # Loop through each bill in bill_list
        for this_bill in bill_list:

            # Create var to take total bill price
            total_bill_price = 0;

            # Bill Header
            self.tape.insert(tk.END, '\n\n');
            self.tape.insert(tk.END, "-" * 15);
            self.tape.insert(tk.END, f"  Bill {this_bill.ID}  ");
            self.tape.insert(tk.END, "-" * 15);

            # Loop through the seat orders of each bill
            for this_seat_order in this_bill.added_orders:

                # Create var to take total order price
                total_order_price = 0;

                # Seat header
                self.tape.insert(tk.END, '\n\n');
                self.tape.insert(tk.END, f'>>> Seat {this_seat_order.get_seat_number()}:');
                self.tape.insert(tk.END, '\n');

                # Loop through all seat orders added menu item
                for this_item in this_seat_order.get_items():

                    # Printing out items
                    self.tape.insert(tk.END, '\n');
                    self.tape.insert(tk.END, f'{this_item.details.name}: ');
                    self.tape.insert(tk.END, '$%.2f' % this_item.details.price);

                    # Add to the total order price
                    total_order_price += this_item.details.price;

                # Print total price of order
                self.tape.insert(tk.END, '\n' + '-' * 27 + '\n');
                self.tape.insert(tk.END, '> TOTAL ORDER PRICE: $%.2f' % total_order_price);
                self.tape.insert(tk.END, '\n');

                # Add to total bill price
                total_bill_price += total_order_price;

            # Print total bill price, and end off the bill.
            self.tape.insert(tk.END, '\n\n');
            self.tape.insert(tk.END, f'> TOTAL PRICE OF BILL {this_bill.ID}: ');
            self.tape.insert(tk.END, '$%.2f' % total_bill_price);
            self.tape.insert(tk.END, '\n\n');


        # Finishing print lines of payment
        self.tape.insert(tk.END, '\n\n\n');
        self.tape.insert(tk.END, "Thank you for coming to Velasco & Mohammed's OORMS restaurant. "
                                 "We hope you enjoyed :).");
        self.tape.insert(tk.END, '\n\n');
        self.tape.insert(tk.END, ">" * 13);
        self.tape.insert(tk.END, " End Payment ");
        self.tape.insert(tk.END, "<" * 13);
        self.tape['state'] = tk.DISABLED
        self.tape.see(tk.END)


    def print_error(self):
        """ Method prints text when an error has occurred in paying the bills. """

        self.tape['state'] = tk.NORMAL
        self.tape.insert(tk.END, '\n')
        self.tape.insert(tk.END, "-" * 40)
        self.tape.insert(tk.END, '\n')
        self.tape.insert(tk.END, 'ERROR OCCURRED WHEN PAYING BILLS. PLEASE TRY AGAIN.');
        self.tape.insert(tk.END, '\n')
        self.tape.insert(tk.END, "-" * 40)
        self.tape['state'] = tk.DISABLED
        self.tape.see(tk.END)


# ------ Defining Functions for drawing Payment and Bill UIs ------

def draw_unassigned_seat_button(canvas, unass_seat_order, anchor, interval, order_interval, handler, index):
    """ For the BILL UI - function draws the text and button for a given unassigned seat object in the right window.

    <canvas : tk.Canvas> : the canvas which the UI is being drawn on.
    <unass_seat_order : Order> : the Order object associated with the unassigned seat to be drawn
    <anchor : (int, int)> : the coordinates of the first Order object being drawn onto the UI. The remaining
        Order objects are to be positioned in relation to this first one.
    <interval: int> : the vertical distance the seat order objects are to be drawn from each other.
    <order_interval: int> : the vertical distance the OrderItems of each seat order are to be drawn from eachother.
    <handler: function> : the handler that is bound to the pressing of the button.
    <index: int> : the index of the unass_seat_order object in the list of unassigned seat orders of the table. """

    # Extracting information to draw seat order
    x_coord, y_coord = anchor;
    seat_num = unass_seat_order.get_seat_number();
    order_items = unass_seat_order.get_items();

    # Drawing out the seat order title (are placed in two columns)
    offset = 0;
    if index > 3:
        offset = 250;
        index -= 4;
    canvas.create_text(x_coord + offset, y_coord + interval * index, text = f'Seat #{seat_num}', anchor = tk.CENTER,
                       font = ("Helvetica", 13, "underline"));

    # Drawing out each seat order's OrderItem objects below its title. Don't print more than 5 lines.
    item_counter = 0;
    for this_item in order_items:

        # Stop loop if more than 5 lines will be printed...
        if item_counter > 4:
            break;
        if item_counter > 3:
            name = "...";
        else:
            name = this_item.details.name;

        # Draw text (x_coord shifted 30 px to left to align accordingly)
        canvas.create_text(x_coord + offset - 30, (y_coord + interval * index) + 20 + (item_counter * order_interval),
                           text = name, anchor = tk.W, font = ("Calibri", 8));

        item_counter += 1;


    # Drawing the plus button associated of the unassigned seat
    # (extra offsets were added to position button accordingly)
    box_style = BUTTON_PLUS_STYLE;
    button = canvas.create_rectangle((x_coord + offset) - 53, (y_coord + interval * index) - 8, (x_coord + offset) - 37,
                                     (y_coord + interval * index) + 8, **box_style);
    plus_vert_line = canvas.create_line((x_coord + offset) - 44, (y_coord + interval * index) - 5,
                                        (x_coord + offset) - 44, (y_coord + interval * index) + 5,
                                        width = 2, fill = '#fff');
    plus_hori_line = canvas.create_line((x_coord + offset) - 49, (y_coord + interval * index), (x_coord + offset) - 39,
                                        (y_coord + interval * index), width = 2, fill = '#fff');

    # Tag binding the button's elements
    canvas.tag_bind(button, '<Button-1>', handler);
    canvas.tag_bind(plus_vert_line, '<Button-1>', handler);
    canvas.tag_bind(plus_hori_line, '<Button-1>', handler);



def draw_bill_info_button(canvas, bill_obj, table_obj, anchor, interval, handler):
    """ For the PAYMENT UI - function draws the text each bill object.

    <canvas : tk.Canvas> : the canvas of which the UI is being drawn on
    <bill_obj : Bill> : the bill object that is being drawn.
    <table_obj : Table> : the Table object bill_obj is stored under.
    <anchor : (int, int)> : the coordinates of the first bill object of the UI being drawn. The remaining
        bill objects are to be positioned in relation to the first one.
    <interval: int> : the vertical and horizontal distance the Bill objects are to be drawn from each other .
    <handler: function> : the handler that is bound to the pressing of this button. """

    # Getting ID of bill object
    ID = bill_obj.ID;

    # Unpacking anchor coordinates
    x_coord, y_coord = anchor;

    # Getting size of half the width and half the height of the button to draw
    half_width = BILL_BUTTON_SIZE[0]/2;
    half_height = BILL_BUTTON_SIZE[1]/2;

    # Determining colour based on status of bill object (if NOT PAID, is white. If PAID, is green).
    curr_status_val = int(bill_obj.get_status());
    box_colours = ['#fff', '#090'];  
    box_style = {'fill': box_colours[curr_status_val], 'outline': '#000'};

    # Find the index of bill_obj within the list Bills of table_obj
    bill_list = table_obj.return_bills();
    this_ind = bill_list.index(bill_obj);

    # Turning the list of added order numbers into strings
    added_orders = [str(order.get_seat_number()) for order in bill_obj.added_orders];
    added_orders.sort();

    # Determining font size of added seats depending on number of added_orders
    if len(added_orders) > 5:
        font_size = 10;
    else:
        font_size = 14;

    # Draw buttons in two rows,
    # Use the int ID of the bill object to place button on first row or second row.
    if this_ind < 4:

        box = canvas.create_rectangle(x_coord + interval * this_ind - half_width, y_coord - half_height,
                                      (x_coord + interval * this_ind) + half_width, y_coord + half_height,
                                      **box_style);
        label = canvas.create_text(x_coord + interval * this_ind, y_coord - 10, text = f'Bill #{ID}',
                                   anchor = tk.CENTER,  font = ("Calibri", 15, 'underline'));
        seats = canvas.create_text(x_coord + interval * this_ind, y_coord + 13, text = ', '.join(added_orders)
                                    , anchor = tk.CENTER, font = ('Times', font_size));

    else:
        box = canvas.create_rectangle(x_coord + interval * (this_ind - 4) - half_width,
                                      y_coord + interval - half_height, (x_coord + interval * (this_ind - 4)) +
                                      half_width, y_coord + half_height + interval, **box_style);
        label = canvas.create_text(x_coord + interval * (this_ind - 4), y_coord + interval - 10, text = f'Bill #{ID}',
                                   anchor = tk.CENTER, font = ("Calibri", 15, 'underline'))
        seats = canvas.create_text(x_coord + interval * (this_ind - 4), y_coord + interval + 13,
                                    text = ', '.join(added_orders), anchor = tk.CENTER,
                                    font = ('Times', font_size));




    # Tag binding the handler to the button elements
    canvas.tag_bind(box, '<Button-1>', handler);
    canvas.tag_bind(label, '<Button-1>', handler);
    canvas.tag_bind(seats, '<Button-1>', handler);




def draw_seat_info(canvas, seat_order, anchor, order_anchor, interval, order_interval):
    """ For the PAYMENT UI - function draws the text for each of the seat orders at the top of the UI.
    An order is only drawn out if it has any order items put in it. 

    <canvas : tk.Canvas > : the canvas of which the UI is being drawn on.
    <seat_order : Order> : the specific order object of the seat whose info is being drawn out.
    <anchor : (int, int)> : the location the first seat order is to be drawn onto the canvas. The remaining
        seat orders are to be positioned in relation to the first one.
    <order_anchor : (int, int)> : the location of where the first item of the first seat order is to be drawn.
        The remaining seat order items for this seat are to be positioned in relation to this anchor.
    <interval : int> : the distance each seat order is to be separated from each other horizontally.
    <order_interval : int> : the distance the order items are to be drawn vertically from each other.
    """

    # Draw out an order only if it has items in it.
    if len(seat_order.get_items()) > 0:

        # Unpacking coordinates from anchors
        x_cood, y_cood = anchor;
        x_order, y_order = order_anchor;

        # Getting the seat number
        seat_num = seat_order.get_seat_number();

        # Getting the width and height of the box to be drawn
        width, height = SEAT_INFO_BOX;

        # Drawing the box of the seat object. (Yes, it extends above the canvas. This was intentional)
        # If seat is UNASSIGNED, colour box white. If ASSIGNED, colour box yellow. If PAID, colour box green.
        curr_status_val = int(seat_order.get_status());
        box_colours = ['#fff', '#ff0', '#090'];  # <-- White -> Yellow -> Green
        box_style = {'fill': box_colours[curr_status_val], 'outline': '#000'};
        box = canvas.create_rectangle((x_cood + interval * seat_num) - width, y_cood - height,
                                      (x_cood + interval * seat_num) + width, y_cood + height, **box_style);

        # Draw the title of the box - literally the seat number
        canvas.create_text(x_cood + interval * seat_num, y_cood, text = "Seat " + str(seat_num), anchor = tk.CENTER,
                           font = ('Times', 11, 'underline'));

        # Drawing the order items made with this seat. Don't print more than 6 items.
        # Using a counter to print items on different lines.
        item_counter = 1;
        for this_item in seat_order.get_items():

            # If there are more than 6 items, have the 7th item be "...", and print no more items
            if item_counter == 7:
                name = "...";
            elif item_counter > 7:
                return;
            else:
                name = this_item.details.name;

            # Drawing the text.
            canvas.create_text(x_order + interval * seat_num - 5, y_order + order_interval * item_counter, text=name,
                                    anchor=tk.W, font=("Calibri", 8));

            item_counter += 1;



# --- Drawing other functions ---

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
    printer_window.geometry(f'{pw}x{ph}+{sx+sw+200}+{sy}')

    root.mainloop()
