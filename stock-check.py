from src.SData import SDataConnection as SData
from src.SQlite import DbConnection as Db
from datetime import datetime


# this class is used to check that the stock levels my system states in the same as sage.
class StockCheck:

    # constructs the class/module by passing in the connection parameters.
    def __init__(self,db,sage):
        """
        Method Name:
            __init__
        Summary:
            this is the main function which automates the whole script/programme .
        Input Parameters:
            db_connection - this is used to connect to the mariaDB server.
            sdata_connection - the connect used to retrieve data from sage.
        Output Parameters:
            NULL
        """
        self.db_connection = db
        self.SDataConnection = sage

    def addProducts(self):
        """
        Method Name:
            addProducts
        Summary:
            adds the products to the test table with updated stock levels.
        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """

        SData = self.SDataConnection
        Db = self.db_connection

        # get all products - return into an 2D array.
        ImportedProducts = SData.get_products()

        # for each product with in the array, we loop through and add them to the mariaDB TEST database.
        for product in ImportedProducts:
            productTmp = [product]
            Db.add_test_product(productTmp)

    def postInvoices(self):
        """
        Method Name:
            postInvoices
        Summary:
            posts invoice into the test database and updates the stock levels accordingly.
            sage does not have a correct stock level, its only as accurate as the stock that is left the building not
            for anything currently on order which is why the system is more complex than expected.
        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """
        SData = self.SDataConnection
        Db = self.db_connection

        # Reads file containing all the non-posted invoice numbers.
        f = open("src/DB/non-posted.txt", "r")
        refs = f.read()
        f.close()

        refs = refs.split(" ")
        refs.pop(0)

        # for each reference we make a request to get the whole order from sage then add/update our db with it.
        for ref in refs:
            orderLines = SData.get_invoice_by_id(ref.rstrip())  # gets order with reference number.
            for orderLine in orderLines:
                Db.update_test_product_stock(orderLine[1], orderLine[2])  # updates the test product stock with it.
                Db.add_test_transaction(orderLine[0], orderLine[1], orderLine[2])  # adds the test transaction to db.

    def stockChecks(self):
        """
        Method Name:
            stockChecks
        Summary:
            the main feature of the programme, checks the useful updates test db stock levels and updates
            the stock on the main if there are any incorrect.
        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """
        Db = self.db_connection

        # selects all products from the test db for cross checking.
        products = Db.get_all_test_products()

        count = 0

        # for each product in the returned array select the main version of the same product.
        for product in products:

            mainProduct = Db.get_product_by_id(product[1])
            TestProduct = Db.get_test_product_by_id(product[1])

            # if the product is not on the main DB add it else more on to comparing stocks.
            if not mainProduct:
                randO = 0
                # print("product not on db")
                # print(TestProduct)
                # Db.add_product(TestProduct)
            else:
                # if the stock levels are not the same we correct them.
                if TestProduct[0][5] - mainProduct[0][5] > 0.1 or TestProduct[0][5] - mainProduct[0][5] < -0.1:
                    count = count + 1
                    print("error TEST db: "+str(TestProduct[0][1])+" has "+str(TestProduct[0][5])+" stock")
                    print(TestProduct)
                    print("error MAIN db: " + str(mainProduct[0][1]) + " has " + str(mainProduct[0][5]) + " stock\n")
                    print(mainProduct)
                    stock = TestProduct[0][5]
                    prdId = TestProduct[0][1]
                    #Db.correct_product_stock(prdId,stock)

        print(str(count)+" incorrect")


# if this file was ran directly it will create the modules/objects/classes and initiate the programme.
if __name__ == "__main__":

    # start time for debugging reasons
    start_time = datetime.now()
    print("start-time: " + str(start_time))

    # db connection modules
    db = Db.DbConnection('192.168.1.94','root','TheOfficePeople',3306,'autoStockCheck')
    SDataCon = SData.SdataConnection('bot01','Bot01','http://192.168.1.200:5495/sdata/accounts50/gcrm/-/')

    # instantiating the stock checker class
    stock_checker = StockCheck(db,SDataCon)

    # running the stock checker class relevant functions.
    #db.delete_test_products()
    #db.delete_test_transactions()
    #stock_checker.addProducts()
    #stock_checker.postInvoices()
    #stock_checker.stockChecks()



