from flask import Flask ,render_template
import sqlite3 as sql

app = Flask(__name__)

@app.route("/")
def homePage ():
    return render_template('index.html')

@app.route("/customers")
def customersPage ():
    with sql.connect("bank_db.db") as con:
    	cur = con.cursor()
    	cur.execute("SELECT * FROM customers;")
    	customers = cur.fetchall()
    return render_template('customers.html',customers=customers)

@app.route("/transaction")
def transactionPage ():
    return render_template('transaction.html')


@app.route('/transferto', methods=['GET','POST'])
def transferto():
	money=int(request.form['money'])
	sender=request.form['sender']
	reciever=request.form['reciever']
	with sql.connect("bank_db.db") as con:
		cur = con.cursor()
		cur.execute(f'select Balance from customers where name="{reciever}"')
		rows=cur.fetchall()
		reciever_balance=rows[0][0]+money
		cur.execute(f'select Balance from customers where name="{sender}"')
		rows=cur.fetchall()
		sender_balance=rows[0][0]-money
		if rows[0][0]<money:
			msg='insufficient balance, transaction failed'
			cur.execute(f'insert into transactions values("{sender}","{reciever}",{money},"failed")')
			con.commit()
			con.rollback()
			return jsonify({'name' : 'error','obj': 'error','msg':msg})
		else:
			try:
				cur.execute(f'UPDATE customers SET balance = {sender_balance} WHERE name="{sender}";')
				cur.execute(f'UPDATE customers SET balance = {reciever_balance} WHERE name="{reciever}";')
			except Exception as e:
				con.rollback()
			con.commit()
			cur.execute(f'select balance from customers where name="{reciever}"')
			rows=cur.fetchall()
			reciever_balance=rows[0][0]
			cur.execute(f'select balance from users where name="{sender}"')
			rows=cur.fetchall()
			sender_balance=rows[0][0]
		cur.execute(f'insert into transactions values("{sender}","{reciever}",{money},"success")')
		con.commit()
		cur.execute('select * from transactions;')
		rows=cur.fetchall()
	return jsonify({'sender' : sender, 'reciever':reciever,'obj': rows,'rb':reciever_balance,'sb':sender_balance})



if __name__ == "__main__":
    app.run('0.0.0.0',debug=True)


