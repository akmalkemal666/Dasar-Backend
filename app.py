from flask import Flask, render_template, request, redirect, url_for, flash
import MySQLdb
import os

app = Flask(__name__)
app.secret_key = "12345"
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="",
    db="crud_upload_db"
)
cursor = db.cursor()


@app.route('/')
def index():
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    limit = 5
    offset = (page - 1) * limit

    if search:
        query = "SELECT * FROM stok WHERE nama LIKE %s LIMIT %s OFFSET %s"
        params = ("%" + search + "%", limit, offset)
        query_count = "SELECT COUNT(*) FROM stok WHERE nama LIKE %s"
        params_count = ("%" + search + "%",)
    else:
        query = "SELECT * FROM stok LIMIT %s OFFSET %s"
        params = (limit, offset)
        query_count = "SELECT COUNT(*) FROM stok"
        params_count = ()

    cursor.execute(query_count, params_count)
    total = cursor.fetchone()[0]
    total_pages = (total // limit) + (1 if total % limit > 0 else 0)

    cursor.execute(query, params)
    data = cursor.fetchall()

    return render_template("index.html",
                           stok=data,
                           page=page,
                           total_pages=total_pages,
                           search=search)


@app.route('/add')
def add():
    return render_template('form.html', action="add")


@app.route('/save', methods=['POST'])
def save():
    kode = request.form['kode']
    nama = request.form['nama']
    harga = request.form['harga']
    file = request.files['file']

    filename = file.filename
    if filename:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    cursor.execute("INSERT INTO stok (kode, nama, harga, filename) VALUES (%s, %s, %s, %s)",
                   (kode, nama, harga, filename))
    db.commit()

    flash("Data berhasil ditambahkan!", "success")
    return redirect(url_for('index'))


@app.route('/edit/<id>')
def edit(id):
    cursor.execute("SELECT * FROM stok WHERE kode=%s", (id,))
    data = cursor.fetchone()
    return render_template('form.html', action="edit", data=data)


@app.route('/update/<id>', methods=['POST'])
def update(id):
    nama = request.form['nama']
    harga = request.form['harga']
    file = request.files['file']

    if file.filename:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor.execute("UPDATE stok SET nama=%s, harga=%s, filename=%s WHERE kode=%s",
                       (nama, harga, filename, id))
    else:
        cursor.execute("UPDATE stok SET nama=%s, harga=%s WHERE kode=%s",
                       (nama, harga, id))

    db.commit()
    flash("Data berhasil diupdate!", "info")
    return redirect(url_for('index'))


@app.route('/delete/<id>')
def delete(id):
    cursor.execute("DELETE FROM stok WHERE kode=%s", (id,))
    db.commit()
    flash("Data berhasil dihapus!", "warning")
    return redirect(url_for('index'))


if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    app.run(debug=True)
