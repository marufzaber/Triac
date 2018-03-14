from flask import Flask, redirect, url_for, request, render_template
from flaskext.mysql import MySQL

mysql = MySQL()


app = Flask(__name__)

def init_db(user, password, database, host):
	app.config['MYSQL_DATABASE_USER'] = user
	app.config['MYSQL_DATABASE_PASSWORD'] = password
	app.config['MYSQL_DATABASE_DB'] = database
	app.config['MYSQL_DATABASE_HOST'] = host
	mysql.init_app(app)
	

#  258399 USES


@app.route('/')
def homepage():
	return render_template('login.html')
	#return redirect(url_for('query_db',query = fqn))
	
# sun.util.resources.el

@app.route('/search' ,methods = ['POST', 'GET'])
def search():
	if request.method == 'POST':
		result = request.form['fqn']		
		cursor = mysql.connect().cursor()
		cursor.execute("SELECT name, project_type, project_id FROM projects where project_id in (SELECT project_id FROM entities WHERE fqn  = '"+result+"')")
		results = cursor.fetchall()
		
		
		cursor.execute("SELECT COUNT(DISTINCT project_id) FROM entities WHERE fqn = '"+result+"'")
		usage = cursor.fetchall()

		use = 1 ;
		for row in usage :
			use = row[0]

		return render_template('result.html', result = results, fqn = result, use = use)


@app.route('/detail/<project_id>/<fqn>')
def detail(project_id, fqn):
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT fqn, entity_type, offset FROM entities WHERE entity_id IN (SELECT lhs_eid FROM relations WHERE rhs_eid IN (SELECT entity_id FROM entities WHERE project_id = "+project_id+" AND fqn = '"+fqn+"') AND project_id = "+project_id+")")
	results = cursor.fetchall()
	cursor.execute("SELECT count(*) from relations where rhs_eid IN (SELECT entity_id FROM entities WHERE project_id = "+project_id+" AND fqn = '"+fqn+"') AND project_id = "+project_id)
	usage = cursor.fetchall()
	
	use = 1 ;
	for row in usage :
		use = row[0]


	return  render_template('detail.html', result = results, fqn = fqn, project_id = project_id, use = use)


			
if __name__ == '__main__':
	init_db('root', 'maruf123', 'sourcerer', 'localhost')
	app.run(debug = True)