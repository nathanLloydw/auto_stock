from src.SData import SDataConnection as SDataConnection
from src.SQlite import DbConnection as Db
from infi.systray import SysTrayIcon
import schedule
from datetime import datetime
import time
import os


# this class manages keeping the stock levels on the mariaDB server correct whilst also storing order history.
class AutoStock:

    # constructs the class/module with the given parameters.
    def __init__(self,db_connection,sdata_connection):
        """
        Method Name:
            __init__
        Summary:
            this is the main function which automates the whole script/programme and manages the system tray.
        Input Parameters:
            db_connection - this is used to connect to the mariaDB server.
            sdata_connection - the connect used to retrieve data from sage.
        Output Parameters:
            NULL
        """
        self.db_connection = db_connection
        self.SDataConnection = sdata_connection

    def build_db(self):
        """
        Method Name:
            build_db
        Summary:
            on the initial run this function can be used to build the several databases used in this system.
        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """

        # Builds the main database used.
        self.db_connection.create_database()

        # creates the tables with in the database.
        self.db_connection.create_database_tables()

    def initial_db_fill(self):
        """
        Method Name:
            initial_db_fill
        Summary:
            after the database has been built this function will migrate all the data from sage to the mariaDB server,
            such as products, customers, suppliers and build a many to many relation between them.
        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """

        # get all products - return into an 2D array.
        products = self.SDataConnection.get_products()

        # for each product with in the array, we loop through and add them to the mariaDB database.
        for product in products:
            print(product)
            self.db_connection.add_product(product)  # add product to DB

        # get all customers - return into an 2D array.
        customers = self.SDataConnection.get_customers()

        # for each customer with in the array, we loop through and add them to the mariaDB database.
        for customer in customers:
            print(customer)
            self.db_connection.add_customer(customer)  # add customer to DB

        # get all suppliers - return into an 2D array.
        suppliers = self.SDataConnection.get_suppliers()

        # for each supplier with in the array, we loop through and add them to the mariaDB database.
        for supplier in suppliers:
            print(supplier)
            self.db_connection.add_supplier(supplier)  # add supplier to DB

        # get all suppliers - return into an 2D array.
        suppliers = self.db_connection.get_suppliers()

        # for each supplier with in the array,
        # we loop through and make a request to sage to retrieve the products they sell.
        for supplier in suppliers:
            print(supplier)
            supplier_id = supplier[0]  # retrieves the supplier ID which is the first entry in the supplier object.

            # retrieves all products we have bought of this supplier - returned as an array
            products = self.SDataConnection.get_orders_in_by_supplier(supplier_id)

            # for each product in the array we then add it to the product_supply table in our DB.
            for product in products:
                print(product)
                product_id = product[0]  # retrieves the product_id from the purchase order model
                product_supplier_price = product[1] # retrieves the cost_price from the purchase order model

                # we then make the request to add this relationship to our DB.
                self.db_connection.add_product_supply(supplier_id,product_id,product_supplier_price)

        # there are duplicates created during this process as you can order a products from a supplier more than once,
        # to fix this we run this function to remove the duplicates.
        self.db_connection.remove_product_supply_duplicates()

        # once all the information has been collected successfully,
        # we trigger the system loop which keeps stock levels correct.
        self.system_loop()

    def system_loop(self):
        """
        Method Name:
            system_loop
        Summary:
            once this function is called it will keep running, calling the necessary functions to keep the DB stock levels
            accurate and record order history.
        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """
        # creating menu options for task bar.
        menu_options = (("Re-Run goodsIn()", None, self.goods_in),
                        ("Re-Run goodsOut()", None, self.goods_out),
                        ("Re-Run checkForEdits()", None, self.check_for_edits))

        # Instantiate & run system tray.
        tray = SysTrayIcon("src/tray/icon.ico", "auto-stock", menu_options, on_quit=on_quit_callback)
        tray.start()

        # notes
        self.set_active_customers()
        # manages orders placed by the customer.
        self.goods_out_automator()
        # manages deliveries and stock replenishment orders.
        self.goods_in_automator()
        # checks customer orders for any edits and updates them & the stock correctly.
        self.check_for_edits()

        # automate the four main functions every 1, 5 & 10 minutes and 6 hours depending on the function.
        schedule.every(1).day.do(self.set_active_customers)
        schedule.every(1).minutes.do(self.goods_out_automator)
        schedule.every(120).minutes.do(self.check_for_edits)
        schedule.every(60).minutes.do(self.goods_in_automator)

        # while true loop, keeps the programming automated.
        while True:
            schedule.run_pending()
            time.sleep(1)

    def set_active_customers(self):
        """
        Method Name:
            set_active_customers
        Summary:
            looks at the customers history to decide upon its activity level which is used to manage priority's.
        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """
        print("\n setting active customers \n")
        db.set_active_customers()
        print("\n set active customers \n")

    def goods_out_automator(self):
        """
        Method Name:
            goods_out_automator
        Summary:
            imports the 5 most recent orders, adds them to the mariaDB database and updates the stock.
        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """

        # authentication details used to access the mariaDB
        db_conn = self.db_connection
        SData = self.SDataConnection

        # Grabs the invoice number which we are working on from a txt file.
        fileRead = open("src/DB/goodsOutNo.txt", "r")
        invoiceNumber = fileRead.read()
        fileRead.close()

        # output for debugging purposes.
        print("\nchecking for new invoices:")
        print("time: "+str(datetime.now()))
        print("order no : "+str(invoiceNumber)+"\n")

        # init variable
        customer = ''

        # calls SData function to retrieve all the order lines between the currentInvoice number and currentInvoice + 5.
        orderLines = SData.get_newest_invoices(invoiceNumber, 10)

        # if the returned value for the previous function doesnt contain any data, print 'no invoices' and function end.
        if not orderLines:
            print("no invoices(orders, returns, refunds etc.)")
        else:
            print("order details : ")
            # we split the returned array from the SData function and look through each entry/orderLine individually.
            for orderLine in orderLines:
                print(orderLine)

                reference = orderLine[0]
                productId = orderLine[1]
                orderQuantity = orderLine[2]
                cost = orderLine[3]
                date = orderLine[4]
                user = orderLine[6]

                if customer != orderLine[5]:
                    print("\ncustomer :"+str(orderLine[5]))
                    db.set_active_customer(orderLine[5],reference)

                customer = orderLine[5]

                # we add this order line as a record on the database,
                # update the stock correctly and update the order number we are on.
                db_conn.add_transactions(productId, orderQuantity,cost, reference,date,customer,user)
                db_conn.remove_product_stock(productId, orderQuantity)
                invoiceNumber = int(reference) + 1

            # write the invoiceNumber we finished on into the text file ready for the next call.
            fileWrite = open("src/DB/goodsOutNo.txt", "w")
            fileWrite.write(str(invoiceNumber))
            fileWrite.close()

            print("next invoice : " + str(invoiceNumber))

    def correct_stock(self,oldOrder,newOrder):
        """
        Method Name:
            correct_stock
        Summary:
            two orders are passed to this function, the current order and the updated version,
            this function updates the Db records and stock levels to match the newest order and not the older one.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
            oldOrder(String[]) : this string[] contains the current order details such as ID, Stock, supplier, quantity etc.
            newOrder(String[]) : this string[] contains the new order details such as ID, Stock, supplier, quantity etc.
        Output Parameters:
            NULL
        """

        # authentication details used to access the mariaDB
        db_conn = self.db_connection

        # instantiate variables to prevent it crashing later on in case they turn out to be empty.
        ref = 0
        date = 0
        customer = 0
        user = 0

        # print variables for debugging purposes.
        print(oldOrder)
        print(newOrder)

        # for each entry/order line in the array/old order we have been passed.
        for order in oldOrder:
            ref = order[0]
            date = order[4]
            customer = order[5]
            user = order[6]
            productId = order[1]
            quantity = order[2]

            # add the stock back to the database that was removed when the order was originally placed.
            db_conn.add_product_stock(productId, quantity)

        # delete the outdated older version of the order from the database.
        db_conn.delete_transactions(ref)

        # for each entry/order line in the array/new order we have been passed.
        for order in newOrder:

            # add the newer/updated version of the order back to the database and update the stock correctly.
            db_conn.add_transactions(order[1], order[2],order[3], ref, date, customer,user)
            db_conn.remove_product_stock(order[1], order[2])

    def check_for_edits(self):
        """
        Method Name:
            check_for_edits
        Summary:
            This function pulls all customer orders in our database which have not left the warehouse and cross checks
            them againest the same order in sage, if they do not match it is replaced with the newer version to keep
            stock levels correct.
        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """

        # authentication details used to access the mariaDB
        db_conn = self.db_connection
        SData = self.SDataConnection

        # output for debugging purposes.
        print("\nchecking for order changes: \n")
        print("time: " + str(datetime.now()))

        # get all the orders references from the database which have not left for delivery.
        references = [x[0] for x in db_conn.get_all_pending_transactions()]
        print(references)

        # for each order reference/string with in reference/array.
        for reference in references:
            # grab a copy of the local order & sage order containing the order reference & instantiate count.
            localLines = db_conn.get_transactions_by_id(reference)
            externalLines = SData.get_invoice_by_id(reference)
            count = 0

            # check if the size of both orders are equal, if not a product has been added or removed.
            if len(localLines) == len(externalLines):

                # while length of the order is smaller than count we look through the counts index in the array
                # for the order lines of the local and sage version of the order.
                while len(externalLines) > count:

                    localLine = localLines[count]
                    externalLine = externalLines[count]

                    # we check if the product and stock both match for each line in the local & sage order,
                    # if not call correct stock function.
                    if localLine[1] != externalLine[1] or int(localLine[2]) != int(externalLine[2]):
                        print("edit in order ref : "+str(reference))
                        self.correct_stock(localLines,externalLines)
                        break
                    else:
                        count = count + 1
            else:
                print("edit in order ref : "+str(reference))
                self.correct_stock(localLines,externalLines)

        print("finished checking for order changes.")

    def goods_in_automator(self):
        """
        Method Name:
            goods_in_automator
        Summary:
            Keeps track of any active/new orders which are in sage to update stock correctly when a new shipment arrives.
        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """

        # authentication details used to access the mariaDB
        db_conn = self.db_connection
        SData = self.SDataConnection

        # instantiate a copy of our current POs in our DB and the current POs with in sage.
        currentPurchaseOrder = db_conn.get_all_active_purchase_orders()
        purchaseOrders = SData.get_active_orders_in()

        # output for debugging purposes.
        print("\nchecking for new/updated purchase orders : ")

        # for each purchase order in purchaseOrders we check if the reference is in our current purchase orders, if not
        # we add it to our database for monitoring during each call.
        for purchaseOrder in purchaseOrders:
            reference = purchaseOrder[0]
            if reference not in [x[0] for x in currentPurchaseOrder]:
                PO = [purchaseOrder]
                db_conn.add_purchase_order(PO)
                print("new po added : "+str(PO[0][0]))

        # for each purchase order in currentPurchaseOrders we check the status of that order on sage
        # and update it correspondingly.
        for purchaseOrder in currentPurchaseOrder:
            reference = purchaseOrder[0]

            # get order status from sage
            status = SData.get_order_in_status(reference)

            # if status is equal to 1 or 4 there is no change
            if status == 1 or status == 4:
                print(str(reference)+" still on order")

            # if status is equal to 2 the order is complete and we update the stock levels on our Db.
            if status == 2:
                print(str(reference)+" complete")

                # before we add the stock to the Db we grab a copy of the order from sage to check the correct quantity
                # was delivered before we update it into the Db.
                completedOrderChecks = SData.get_order_in_details_by_id(reference)
                for compOrder in completedOrderChecks:
                    product_Id = compOrder[0]
                    stock = compOrder[2]
                    db_conn.update_purchase_order_stock(reference,product_Id,stock)

                # update the stock delivered into our current stock and update the order status correspondingly.
                completedOrders = db_conn.get_purchase_order_by_id(reference)
                for completedOrder in completedOrders:
                    ordId = completedOrder[0]
                    supplier = completedOrder[5]
                    productId = completedOrder[6]
                    stock = completedOrder[7]
                    print("    "+str(productId)+" : "+str(stock))
                    db_conn.add_product_stock(productId,stock)
                    db_conn.add_transactions(productId, (0 - stock), 0, ordId, datetime.now(), supplier, 'goods-in')
                db_conn.update_purchase_order_by_id(reference,'complete')

            # if status is equal to 3 it has been cancelled and we update the order to state that.
            elif status == 3:
                print(str(purchaseOrder[0])+" cancelled")
                db_conn.update_purchase_order_by_id(purchaseOrder[0],'cancelled')

        print("\nPurchase Orders updated")

    def add_all_purchase_orders(self):
        """
        Method Name:
            add_all_purchase_orders
        Summary:
            connects to sage to retrive all purchase orders, loops through the returned data and adds it to mariaDB.
        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """

        orders = self.SDataConnection.get_orders_in()
        for order in orders:
            print(order)
            reference = order[0]
            status = order[1]
            order_date = order[2]
            due_date = order[3]
            user = order[4]
            supplier_id = order[5]
            product_id = order[6]
            quantity = order[7]
            self.db_connection.add_purchase_order((reference,status,order_date,due_date,user,supplier_id,product_id,quantity))

    def goods_in(self,tray):
        self.goods_in_automator()

    def goods_out(self,tray):
        self.goods_out_automator()

    def editchecks(self,tray):
        self.check_for_edits()


def on_quit_callback(tray):
    os.abort()
    print("application quit.")


# if this file was ran directly it will create the modules/objects/classes and initiate the programme.
if __name__ == "__main__":
    db = Db.DbConnection('192.168.1.94','root','TheOfficePeople',3306,'autoStock')
    SDataCon = SDataConnection.SdataConnection('bot01','Bot01','http://192.168.1.200:5495/sdata/accounts50/gcrm/-/')
    auto_stock = AutoStock(db,SDataCon)
    auto_stock.system_loop()

