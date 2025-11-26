from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
Bootstrap(app)

# -----------------------------
# Koneksi ke MongoDB
# -----------------------------
client = MongoClient("mongodb://localhost:27017/")  # Ubah jika pakai Atlas
db = client["crud_database"]
collection = db["items"]

# -----------------------------
# HOME – Menampilkan Semua Data
# -----------------------------
@app.route("/")
def index():
    items = list(collection.find())
    return render_template("index.html", items=items)

# -----------------------------
# ADD – Tambah Data Baru
# -----------------------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        kode = request.form["kode"]
        nama = request.form["nama"]
        harga = request.form["harga"]
        jumlah = request.form["jumlah"]

        # Insert ke MongoDB
        collection.insert_one({
            "kode": kode,
            "nama": nama,
            "harga": harga,
            "jumlah": jumlah
        })

        return redirect(url_for("index"))

    return render_template("add.html")
@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    item = collection.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        kode = request.form["kode"]
        nama = request.form["nama"]
        harga = request.form["harga"]
        jumlah = request.form["jumlah"]

        collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "kode": kode,
                "nama": nama,
                "harga": harga,
                "jumlah": jumlah
            }}
        )
        return redirect(url_for("index"))

    return render_template("edit.html", item=item)

# -----------------------------
# Hapus Data
# -----------------------------
@app.route("/delete/<id>")
def delete(id):
    collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("index"))

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
