from datetime import date
import mysql.connector as maria

class DbConnection:

    def __init__(self,host,user,password,port,database):
        self.db = maria.connect(host=host, user=user, port=port, password=password,database=database)

    def create_database(self):
        """
        Method Name:
            create_database
        Summary:
            creates a database in the server called autostock.
        Input Parameters:
            null
        Output Parameters:
            null
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        cursor.execute("CREATE DATABASE autostock; CREATE DATABASE autostockcheck")

        db_conn.commit()

    def create_database_tables(self):
        """
        Method Name:
            create_database_tables
        Summary:
            creates tables with in the database.
        Input Parameters:
            null
        Output Parameters:
            null
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        cursor.execute("CREATE TABLE autostock.customers (uuid Text,customer_id Text,company_name Text, alocation Text,address Text,town_city Text,post_code Text)")
        cursor.execute("CREATE TABLE autostock.products (uuid Text,product_id Text, product_name Text, sales_rice Bool,cost_price Bool, stock Int)")
        cursor.execute("CREATE TABLE autostock.suppliers (supplier_id Text, supplier_name Text, contact_name Text, contact_type Text, telephone Int, email Text)")
        cursor.execute("CREATE TABLE autostock.product_supply (supplier Text, product Text, cost Double)")
        cursor.execute("CREATE TABLE autostock.purchase_orders (order_reference Text, order_status Text, order_date DateTime, due_date DateTime, user Text, supplier_id Text, product_id Text, Quantity Bool)")
        cursor.execute("CREATE TABLE autostock.transactions (order_reference Text, product_id Text, quantity Bool, sales_price Bool, delivery_date DateTime, customer_id Text, user Text)")

        cursor.execute("CREATE TABLE autostockcheck.products (uuid Text,product_id Text, product_name Text, sales_rice Bool,cost_price Bool, stock Int)")
        cursor.execute("CREATE TABLE autostockcheck.transactions (order_reference Text, product_id Text, quantity Bool, sales_price Bool, delivery_date DateTime, customer_id Text, user Text)")

        db_conn.commit()

    def add_purchase_order(self,order):
        """
        Method Name:
            add_purchase_order
        Summary:
            adds a purchase order to the database
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """
        db_conn = self.db
        cursor = db_conn.cursor()

        order = order[0]
        orderdate = order[2]
        duedate = order[3]

        cursor.execute("INSERT INTO purchase_orders VALUES ('"+str(order[0])+"', 'On Order','"+str(orderdate)+"','"+str(duedate)+"','"+str(order[4])+"','"+str(order[5])+"','"+str(order[6])+"', "+str(order[7])+")")
        db_conn.commit()

    def add_transactions(self,productId,orderQuantity,cost,reference,date,customer,user):
        """
        Method Name:
            add_transactions
        Summary:
            adds transaction to the database.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """
        db_conn = self.db
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO transactions VALUES ('"+str(reference)+"','"+str(productId)+"',"+str(orderQuantity)+","+str(cost)+",'"+str(date)+"','"+str(customer)+"','"+str(user)+"')")

        db_conn.commit()

    def add_product_supply(self,supplier_id,product_id,product_cost):
        """
        Method Name:
            add_product_supply
        Summary:
            adds a product supply relation to the db.
        Input Parameters:
            NULL
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """
        db_conn = self.db
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO product_supply VALUES ('"+str(supplier_id)+"','"+str(product_id)+"',"+str(product_cost)+")")

        db_conn.commit()

    def add_product_stock(self,product_id,quantity):
        """
        Method Name:
            add_product_stock
        Summary:
            adds stock to a products current stock level.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        sql = "UPDATE products SET Stock = Stock + "+str(quantity)+" where product_id='"+str(product_id)+"'"

        cursor.execute(sql)
        db_conn.commit()

    def remove_product_stock(self,product_id,quantity):
        """
        Method Name:
            remove_product_stock
        Summary:
            removes stock from a products current stock level.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        sql = "UPDATE products SET Stock = Stock - "+str(quantity)+" where product_id='"+str(product_id)+"'"

        cursor.execute(sql)
        db_conn.commit()

    def remove_product_supply_duplicates(self):
        """
        Method Name:
            remove_product_supply_duplicates
        Summary:
            tbc
        Input Parameters:
            null
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        sql = """CREATE TABLE product_supply_tmp LIKE product_supply;
                 INSERT INTO product_supply_tmp (SELECT supplier,product,cost FROM product_supply GROUP BY supplier,product,cost);
                 DELETE DROP table product_supply;
                 RENAME TABLE product_supply_tmp TO product_supply;"""

        cursor.execute(sql)
        db_conn.commit()

    def update_purchase_order_stock(self,reference,productId,Stock):
        """
        Method Name:
            update_purchase_order_stock
        Summary:
            updates a purchase order stock level before we accept and add it to the db.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        sql = "update purchase_orders set Quantity="+str(Stock)+" where order_reference='" + str(reference) + "' and product_id='"+str(productId)+"'"

        cursor.execute(sql)
        db_conn.commit()

    def add_supplier_uuid(self,uuid,product_id):
        """
        Method Name:
            update_purchase_order_stock
        Summary:
            updates a purchase order stock level before we accept and add it to the db.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        sql = "update suppliers set uuid='" + str(uuid) + "' where supplier_id='" + str(product_id)+"'"
        cursor.execute(sql)
        db_conn.commit()

    def get_purchase_order_by_id(self,OrdId):
        """
        Method Name:
            get_purchase_order_by_id
        Summary:
            returns a purchase order by the given ID.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("select * from purchase_orders where order_reference='"+str(OrdId)+"'")
        db_conn.commit()
        return cursor.fetchall()

    def get_all_product_supplys(self):
        """
        Method Name:
            get_all_product_supplys
        Summary:
            returns all product supplys
        Input Parameters:

        Output Parameters:

        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("select * from product_supply")
        db_conn.commit()
        return cursor.fetchall()

    def get_all_products(self):
        """
        Method Name:
            get_all_products
        Summary:
            returns all products in DB.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("SELECT * FROM products")
        db_conn.commit()
        return cursor.fetchall()

    def get_all_pending_transactions(self):
        """
        Method Name:
            get_all_pending_transactions
        Summary:
            gets all transactions from the DB which have not reach the due date yet/posted(N)
        Input Parameters:
            null
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)

        cursor.execute("SELECT DISTINCT order_reference FROM transactions WHERE delivery_date > adddate(NOW(),-1)")
        db_conn.commit()

        return cursor.fetchall()

    def get_transactions_by_id(self,ref):
        """
        Method Name:
            get_transactions_by_id
        Summary:
            returns all transactions which have the order reference given.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("SELECT * FROM transactions where order_reference='"+str(ref)+"'")
        db_conn.commit()
        return cursor.fetchall()

    def get_suppliers(self):
        """
        Method Name:
            get_suppliers
        Summary:
            returns all suppliers
        Input Parameters:
            null
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("SELECT * FROM suppliers")
        db_conn.commit()
        return cursor.fetchall()

    def get_product_supply_lead_time(self,supplier,product):
        """
       Method Name:
           get_product_supply_lead_time
       Summary:
           returns lead time
       Input Parameters:
           null
       Output Parameters:
           null
       """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        sql = """SELECT supplier_id,product_id,max(lead_time) AS lead_time FROM 
                 (
                   SELECT *,datediff(DATE(due_date),order_date) AS lead_time FROM purchase_orders WHERE due_date != 'n/a' 
                   AND datediff(DATE(due_date),order_date) > 0 AND product_id='"""+str(product)+"""' AND supplier_id='"""+str(supplier)+"""'
                 ) 
                 AS F GROUP BY supplier_id,product_id"""

        cursor.execute(sql)
        db_conn.commit()
        return cursor.fetchall()

    def get_all_active_purchase_orders(self):
        """
        Method Name:
            get_all_active_purchase_orders
        Summary:
            gets all purchase orders which are current active.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("SELECT DISTINCT order_reference FROM purchase_orders WHERE order_status='On Order'")
        db_conn.commit()
        return cursor.fetchall()

    def update_purchase_order_by_id(self,ref,status):
        """
        Method Name:
            update_purchase_order_by_id
        Summary:
            updates a purchase orders status to complete or cancelled depending on the given reference and status.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("update purchase_orders SET order_status='"+str(status)+"' WHERE order_reference="+str(ref))
        db_conn.commit()

    def set_active_customers(self):
        """
        Method Name:
            set_active_customers
        Summary:

        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("UPDATE customers SET STATUS = 1 WHERE STATUS = 4 OR STATUS = 3 OR STATUS = 2")
        cursor.execute("""UPDATE customers
                            INNER JOIN 
                            (
                              SELECT t.customer_id,last_order,days_since_order FROM
                              (
                                SELECT customer_id,max(delivery_date) AS last_order,DATEDIFF(NOW(),max(delivery_date)) AS days_since_order from transactions WHERE DATEDIFF(NOW(),delivery_date) < 50 and LEFT(customer_id,2) != 'ZZ' GROUP BY customer_id
                              )
                              AS t
                              INNER JOIN customers AS c ON c.customer_id=t.customer_id ORDER BY post_code
                            )
                            AS f ON f.customer_id=customers.customer_id
                            SET customers.status = 4
                        """)

        cursor.execute("""UPDATE customers
                            INNER JOIN 
                            (
                                SELECT t.customer_id,last_order,days_since_order FROM
                                (
                                  SELECT customer_id,max(delivery_date) AS last_order,DATEDIFF(NOW(),max(delivery_date)) AS days_since_order from transactions WHERE DATEDIFF(NOW(),delivery_date) < 1 and LEFT(customer_id,2) != 'ZZ' GROUP BY customer_id
                                )
                                AS t
                                INNER JOIN customers AS c ON c.customer_id=t.customer_id ORDER BY post_code
                            )
                            AS f ON f.customer_id=customers.customer_id
                            SET customers.status = 2 where status != 0
                        """)
        db_conn.commit()

    def set_active_customer(self,customer_id,reference):
        """
        Method Name:
            set_active_customer
        Summary:

        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("update customers SET status=2 WHERE customer_id='" + str(customer_id)+"' and status != 0")
        cursor.execute("update customers SET last_order_ref='"+str(reference)+"', last_order_date= now() WHERE customer_id='" + str(customer_id) + "' and status != 0")
        db_conn.commit()

    def update_customer_phone(self,customer_id,phone_num):
        """
        Method Name:
            update_customer_phone
        Summary:

        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """
        phone_num = phone_num.replace("'",'')
        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("update customers set phone='"+str(phone_num)+"' where customer_id='"+str(customer_id)+"'")
        db_conn.commit()

    def update_product_weight(self,product_id,weight):
        """
        Method Name:
            update_customer_phone
        Summary:

        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("update products set weight="+str(weight)+" where product_id='"+ str(product_id)+"'")
        db_conn.commit()

    def update_product_supply(self,supplier,product,lead_time):
        """
        Method Name:
            update_product_supply
        Summary:

        Input Parameters:
            NULL
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute(
            "update product_supply SET lead_time=" + str(lead_time) + " WHERE product_id='" + str(product)+"' and supplier_id='"+str(supplier)+"'")
        db_conn.commit()

    def delete_transactions(self,ref):
        """
        Method Name:
            delete_transactions
        Summary:
            deletes transaction records.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM transactions where order_reference='"+ref+"'")
        db_conn.commit()

    def update_transactions_by_date(self):
        """
        Method Name:
            update_transactions_by_date
        Summary:
            updates all transactions to posted if the date is less than todays.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        cursor.execute("update transactions SET posted='yes' WHERE DATE < adddate(NOW(),-1) AND posted='no'")
        db_conn.commit()

    def update_customer_address_by_id(self,id,address,townCity,postCode):
        """
        Method Name:
            update_customer_address_by_id
        Summary:
            updates the customers shipping details
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
            id(String) : The Unique Identifier for the customer we will be updating.
            address(String) : The address the customer is based.
            townCity(String) : The town or city the customer is based.
            postCode(String) : the post code the customer is based in.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        cursor.execute("update customers SET address='"+str(address)+"', townCity='"+str(townCity)+"', postCode='"+str(postCode)+"' WHERE customerId='"+str(id)+"'")
        db_conn.commit()

    def update_product_cost_price(self,product_id,cost_price):
        """
        Method Name:
            update_product
        Summary:
            adds the cost price to the database where the id is equal to the given id.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
            PrdID(String) : The Unique Identifier for the product we will be updating.
            Quantity(Int) : The amount we can buy the product for or bought for last time.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        sql = "update autostock.products set costPrice = "+str(cost_price)+" where product_id='"+str(product_id)+"'"
        cursor.execute(sql)
        db_conn.commit()

    def update_product_uuid(self,id,uuid):
        """
        Method Name:
            update_product_uuid
        Summary:
            updates the product back end unique identifier.
        Input Parameters:
            id(String) : this is the id used to identify the product on the front end.
            uuid(String) : this is the id used to identify the product through code.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        sql = "update autostock.products set uuid = '" + str(uuid) + "' where product_id='" + str(id) + "'"
        cursor.execute(sql)
        db_conn.commit()

    def update_customer_uuid(self,id,uuid):
        """
        Method Name:
            update_customer_uuid
        Summary:
            updates the customers back end unique identifier.
        Input Parameters:
            id(String) : this is the id used to identify the customer on the front end.
            uuid(String) : this is the id used to identify the customer through code.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        sql = "update autostock.customers set uuid = '" + str(uuid) + "' where customerId='" + str(id) + "'"
        cursor.execute(sql)
        db_conn.commit()

    def add_product(self,product):
        """
        Method Name:
            add_product
        Summary:
            adds a new product to the database.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
            product(String[]) : product details such as ID, Name, stock & price.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()

        product = product[0]

        cursor.execute("insert into autostock.products VALUES ('"+str(product[0])+"', '"+str(product[1])+"', '"
                       +str(product[2].replace("'",'').replace('"',''))+"', "+str(product[3])+", "+str(product[4])+", "+str(product[5])+")")

        db_conn.commit()

    def add_customer(self,customer):
        """
        Method Name:
            add_customer
        Summary:
            adds a new product to the database.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
            customer(String[]) : customer details such as ID, Name, address.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        cursor.execute("insert into autostock.customers VALUES ('"+str(customer[0])+"', '"+str(customer[1])+"', '"
                       +str(customer[2].replace("'",''))+"', '"+str(customer[3])+"', '"+str(customer[4].replace("'",''))+"', '"+str(customer[5])+"','"
                       +str(customer[6].replace("'",''))+"')")

        db_conn.commit()

    def add_supplier(self,supplier):
        """
        Method Name:
            add_supplier
        Summary:
            adds a new product to the database.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
            supplier(String[]) : supplier details such as ID, Name, address.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        cursor.execute("insert into autostock.suppliers VALUES ('"+str(supplier[0])+"', '"+str(supplier[1].replace("'",''))+"', '"+str(supplier[2].replace("'",''))+"', '"+str(supplier[3])+"', '"+str(supplier[4])+"', '"+str(supplier[5])+"')")
        db_conn.commit()

    def get_product_by_id(self,PrdId):
        """
        Method Name:
            get_product_by_id
        Summary:
            gets a product from the database which matches the ID passed.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
            PrdId(String) : The Unique Identifier for the product we are looking for.
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("select * from autostock.products where product_id='"+str(PrdId)+"'")
        db_conn.commit()
        return cursor.fetchall()

    def correct_product_stock(self,PrdId,stock):
        """
            Method Name:
                correct_product_stock
            Summary:
                updates all product stock to the correct value.
            Input Parameters:
                db_conn(String[]) : this contains the authentication details to access the mariaDB server.
                PrdID(String) : The Unique Identifier for the product we will be updating.
                Stock(Int) : The corrected stock value.
            Output Parameters:
                NULL
            """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("UPDATE autostock.products SET stock="+str(stock)+" WHERE product_id='"+str(PrdId)+"'")
        db_conn.commit()

# ================================================= Test Functions =====================================================

    def add_test_product(self,product):
        """
        Method Name:
            add_test_product
        Summary:
            updates all product stock to the correct value.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
            product(String[]) : product details such as ID, Name, stock & price.
        Output Parameters:
            NULL
        """
        product = product[0]
        print(product)
        db_conn = self.db
        cursor = db_conn.cursor()
        cursor.execute("insert into autostockcheck.products VALUES ('"+str(product[0])+"', '"+str(product[1])+
                       "', '"+str(product[2].replace("'",''))+"', "+str(product[3])+", "+str(product[4])+", "+str(product[5])+")")
        db_conn.commit()

    def add_test_transaction(self,ref,product_id,quantity):
        """
            Method Name:
                add_test_transaction
            Summary:
                adds a product transaction to the database.
            Input Parameters:
                db_conn(String[]) : This contains the authentication details to access the mariaDB server.
                ref(String) : The reference to the order the transaction took place.
                product_id(String) : The ID to the product which we are recording a transaction for.
                quantity(Int) : The amount of the product which was involved in the transaction.
            Output Parameters:
                NULL
            """

        db_conn = self.db
        cursor = db_conn.cursor()
        sql = "INSERT INTO autostockcheck.transactions values('"+str(ref)+"','"+str(product_id)+"',"+str(quantity)+")"
        cursor.execute(sql)
        db_conn.commit()

    def update_test_product_stock(self,product_id,quantity):
        """
            Method Name:
                update_test_product_stock
            Summary:
                updates the products stock level.
            Input Parameters:
                db_conn(String[]) : this contains the authentication details to access the mariaDB server.
                PrdID(String) : The Unique Identifier for the product we will be updating.
                Quantity(Int) : The amount we will be removing or add from the product Stock.
            Output Parameters:
                NULL
            """

        db_conn = self.db
        cursor = db_conn.cursor()
        sql = "update autostockcheck.products set stock = stock -"+str(quantity)+" where product_id='"+str(product_id)+"'"
        cursor.execute(sql)
        db_conn.commit()

    def get_all_test_products(self):
        """
        Method Name:
            get_all_test_products
        Summary:
            gets all the test products from the database.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("SELECT * FROM autostockcheck.products")
        db_conn.commit()
        return cursor.fetchall()

    def get_test_product_by_id(self,PrdID):
        """
        Method Name:
            get_test_product_by_id
        Summary:
            gets a product which contains the PrdID passed.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
            PrdID(String) : The Unique Identifier for the product we retrieving.
        Output Parameters:
            json_data(JSON) : the resulting json data it returned to where it was called to be decoded.
        """

        db_conn = self.db
        cursor = db_conn.cursor(buffered=True)
        cursor.execute("SELECT * FROM autostockcheck.products WHERE product_id ='"+str(PrdID)+"'")
        db_conn.commit()
        return cursor.fetchall()

    def delete_test_products(self):
        """
            Method Name:
                delete_test_products
            Summary:
                deletes all test products from the database.
            Input Parameters:
                db_conn(String[]) : this contains the authentication details to access the mariaDB server.
            Output Parameters:
                NULL
            """

        db_conn = self.db
        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM  autostockcheck.products")
        db_conn.commit()

    def delete_test_transactions(self):
        """
        Method Name:
            delete_test_transactions
        Summary:
            deletes all test transactions from the database.
        Input Parameters:
            db_conn(String[]) : this contains the authentication details to access the mariaDB server.
        Output Parameters:
            NULL
        """

        db_conn = self.db
        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM autostockcheck.transactions")
        db_conn.commit()

