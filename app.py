from flask import Flask, redirect, url_for, request, render_template
from flaskext.mysql import MySQL

mysql = MySQL()


app = Flask(__name__)

file = {}


def init_db(user, password, database, host):
	app.config['MYSQL_DATABASE_USER'] = user
	app.config['MYSQL_DATABASE_PASSWORD'] = password
	app.config['MYSQL_DATABASE_DB'] = database
	app.config['MYSQL_DATABASE_HOST'] = host
	mysql.init_app(app)
	
def init_index():
	cursor = mysql.connect().cursor()
	cursor.execute("select file_id, name from files")
	results = cursor.fetchall()
	for row in results:
		file[row[0]] = row[1]


@app.route('/')
def homepage():
	return render_template('login.html')
	

@app.route('/search' ,methods = ['POST', 'GET'])
def search():
	if request.method == 'POST':
		result = request.form['fqn']		
		cursor = mysql.connect().cursor()


		cursor.execute("SELECT name, project_type, project_id FROM projects where project_id in (SELECT project_id FROM entities WHERE fqn  = '"+result+"')")
		results = cursor.fetchall()
		
		library_count = 0
		project_count = 0

		use = {}

		for row in results:
			if row[1] == 'JAVA_LIBRARY':
				library_count+=1
			else:
				project_count+=1
			cursor.execute("SELECT COUNT(lhs_eid) FROM relations WHERE project_id = "+str(row[2])+" AND rhs_eid IN (SELECT entity_id FROM entities WHERE fqn ='"+result+"' AND project_id ="+str(row[2])+")")
			count = cursor.fetchall()

			for row1 in count:
				use[row[0]] = row1[0]
				

		return render_template('result.html', result = results, fqn = result, library = library_count , project = project_count, use = use)


@app.route('/detail/<project_id>/<fqn>')
def detail(project_id, fqn):
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT fqn, entity_type, offset, file_id FROM entities WHERE entity_id IN (SELECT lhs_eid FROM relations WHERE rhs_eid IN (SELECT entity_id FROM entities WHERE project_id = "+project_id+" AND fqn = '"+fqn+"') AND project_id = "+project_id+")")
	results = cursor.fetchall()
	cursor.execute("SELECT COUNT(DISTINCT lhs_eid) from relations where rhs_eid IN (SELECT entity_id FROM entities WHERE project_id = "+project_id+" AND fqn = '"+fqn+"') AND project_id = "+project_id)
	usage = cursor.fetchall()
	
	use = 1 ;
	for row in usage :
		use = row[0]

	cursor.execute("SELECT name from projects WHERE project_id = "+project_id)

	proj = cursor.fetchall()
	project_name = ""
	for row in proj:
		project_name = row[0]


	return  render_template('detail.html', result = results, fqn = fqn, project_id = project_id, use = use, project_name = project_name, file=file)


			
if __name__ == '__main__':
	init_db('root', 'maruf123', 'nnsourcerer', 'localhost')
	init_index()
	app.run(debug = True)