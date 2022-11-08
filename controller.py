"""

    Description:

    Provides the controller layer for the OORMS system.

    Notes:
        - None for now


    Submitting lab group: OCdt Al-Ansar Mohammed, OCdt Velasco
    Submission date: November 24th, 2022

    Original code by EEE320 instructors.

"""


class Controller:

    def __init__(self, view, restaurant):
        """ Constructor of Controller object.

        <view> is a RestaurantView object that handles all the drawing of the user interfaces of its child classes,
        and <restaurant> is a Restaurant object which contains all the data used to draw out the tables, chairs,
        and orders. """

        self.view = view
        self.restaurant = restaurant


class RestaurantController(Controller):
    """ Controller for the restaurant view in the ServerView object. """

    def create_ui(self):
        """ Calling .create_ui() method from this class back in the ServerView object calls the create_restaurant_ui().
        Essentially calls the method to draw the entire restaurant into the canvas. """

        self.view.create_restaurant_ui()


    def table_touched(self, table_number):
        """ Sets the current controller of the ServerView object to the TableController
        associated with the table of <table_number>.  """
        self.view.set_controller(TableController(self.view, self.restaurant,  self.restaurant.tables[table_number]))
        self.view.update()



class TableController(Controller):
    """ Controller for the view of a given table within the restaurant in the ServerView object. """

    def __init__(self, view, restaurant, table):
        """ Constructor of TableController object.

        <view> is a ServerView object that handles all the drawing of the user interfaces, <restaurant>
        is the Restaurant object which contains all the data used to draw out the tables, chairs, and orders,
        <table> is a specific table object that was clicked on. """

        super().__init__(view, restaurant)
        self.table = table


    def create_ui(self):
        """ Calling .create_ui() method calls the create_table_ui() back in the user interface.
        Essentially draws the specific table and associated chairs of this TableController onto the canvas. """
        self.view.create_table_ui(self.table)

    def seat_touched(self, seat_number):
        """ Sets the current controller of the ServerView window to be the OrderController associated with the
        seat that just touched - opens up the order menu of the corresponding chair.  """
        self.view.set_controller(OrderController(self.view, self.restaurant, self.table, seat_number))
        self.view.update()

    def make_bills(self, printer):

        # TODO: switch to appropriate controller & UI so server can create and print bills
        # for this table. The following line illustrates how bill printing works, but the
        # actual printing should happen in the (new) controller, not here.

        # Switching the payment controller of the bill pressed
        self.view.set_controller(PaymentController(self.view, self.table, self.restaurant));
        self.view.update();

        # Print shit in the printer
        printer.print(f'Set up bills for table {self.restaurant.tables.index(self.table)}')


    def done(self):
        """ Method returns the controller back to RestaurantController - setting the user interface back
        to the view of the restaurant. """
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()


class OrderController(Controller):

    def __init__(self, view, restaurant, table, seat_number):
        """ Constructor of OrderController object.

        <view> is a ServerView object that handles all the drawing of the user interfaces, <restaurant>
        is the Restaurant object which contains all the data used to draw out the tables, chairs, and orders,
        <table> is a specific table object that was clicked on, <seat_number> is the number of the seat at the table
        that was clicked on. """

        super().__init__(view, restaurant)
        self.table = table
        self.order = self.table.order_for(seat_number)


    def create_ui(self):
        """ Calling .create_ui() method calls the create_table_ui() back in the user interface.
        Essentially draws the order menu associated with the specific chair touched onto the canvas. """
        self.view.create_order_ui(self.order)

    def add_item(self, menu_item):
        """ Method that adds item to the "to be ordered" list when the order user interface is up.

        Function does this by adding the item through the Order object's .add_item() method, and
        updates the order user_interface by calling view.update().  """
        self.order.add_item(menu_item)
        self.restaurant.notify_views()

    def remove(self, order_item):
        """ Method removes passed in <order_item> from the table's order. """
        self.order.remove_item(order_item)
        self.restaurant.notify_views()

    def update_order(self):
        """ Method responsible for placing the requested orders into the PLACED status and set its __ordered attribute
        to True. Furthermore, placed orders show up in the KitchenView window, and ServerView returns to the table
        that was previously click on. """
        self.order.place_new_orders()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.restaurant.notify_views()

    def cancel_changes(self):
        """ Method is responsible for cancelling an order whose items have yet to be placed (still in REQUESTED status).

        Method is called when 'Cancel' button in order user interface is pressed. After pressing, returns ServerView
        to the table associated with the chair whose order was just cancelled. """
        self.order.remove_unordered_items()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.restaurant.notify_views()


class PaymentController(Controller):
    """ Handles events from the Payment UI. """


    # Idk if we need this.
    def __init__(self, view, table, restaurant):
        """ Class constructor. """

        # Saving the objects passed through args
        self.table = table;
        self.restaurant = restaurant;

        # Superclass constructor
        super().__init__(view, table);


    def create_ui(self):
        """ Legit creates ui back in the view. """
        self.view.create_payment_ui();


    def fuck_around_pressed(self):
        """ Legit the handler when fuck around button gets pressed. """

        # do the fuck around shit
        self.view.fuck_payment_update();


    def exit_pressed(self):
        """ Handler that exits Payment UI back to table view. """
        self.view.set_controller(TableController(self.view, self.restaurant, self.table));
        self.view.update()



class BillController(Controller):
    """ Handles events from the Bill UI. """

    def create_ui(self):
        """ legit creates ui back in the view. """
        self.view.create_bill_ui();


    # ...