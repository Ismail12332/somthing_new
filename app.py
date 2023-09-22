import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()


def create_app(*args, **kwargs):
    app = Flask(__name__, template_folder='templates')
    app.config['DEBUG'] = True 
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["myapp_db"]


    @app.route("/")
    def index():
        sections = db.sections.find()
        return render_template("index.html", sections=sections)


    @app.route("/add_section", methods=["POST"])
    def add_section():
        section_name = request.form.get("section_name")
        db.sections.insert_one({"name": section_name, "subsections": []})
        return redirect(url_for("index"))


    @app.route("/add_subsection/<section_id>/subsection", methods=["POST"])
    def add_subsection(section_id):
        subsection_name = request.form.get("subsection_name")
        print(f"section_id: {section_id}")
        subsection_id = ObjectId()  # Генерируем новый ObjectId для подраздела
        db.sections.update_one({"_id": ObjectId(section_id)}, {"$push": {"subsections": {"_id": subsection_id, "name": subsection_name, "descriptions": []}}})
        return redirect(url_for("index"))

    # ...

    @app.route("/add_description/<section_id>/<subsection_id>", methods=["POST"])
    def add_description(section_id, subsection_id):
        section_id = ObjectId(section_id)
        subsection_id = ObjectId(subsection_id)
        
        # Получаем текстовое описание из формы
        description_text = request.form.get("description")
        
        # Генерируем новый ObjectId для описания
        description_id = ObjectId()
        
        # Создаем объект описания с текстом
        description = {"_id": description_id, "text": description_text}
        
        db.sections.update_one(
            {"_id": section_id, "subsections._id": subsection_id},
            {"$push": {"subsections.$.descriptions": description}}
        )
        
        return redirect(url_for("index"))

    @app.route("/add_rating/<section_id>/<subsection_id>", methods=["POST"])
    def add_rating(section_id, subsection_id):
        section_id = ObjectId(section_id)
        subsection_id = ObjectId(subsection_id)
        
        # Получаем рейтинг из формы
        description_rating = request.form.get("description_rating")
        
        # Генерируем новый ObjectId для рейтинга
        rating_id = ObjectId()
        
        # Создаем объект рейтинга
        rating = {"_id": rating_id, "rating": description_rating}
        
        db.sections.update_one(
            {"_id": section_id, "subsections._id": subsection_id},
            {"$push": {"subsections.$.ratings": rating}}
        )
        
        return redirect(url_for("index"))




    #Раздел удаления разделов секций подсекций

    # Удалиние раздела
    @app.route("/delete_section/<section_id>", methods=["POST"])
    def delete_section(section_id):
        section_id = ObjectId(section_id)
        
        # Удалите раздел из базы данных
        db.sections.delete_one({"_id": section_id})
        
        return redirect(url_for("index"))

    # Удалиние подраздела
    @app.route("/delete_subsection/<section_id>/<subsection_id>", methods=["POST"])
    def delete_subsection(section_id, subsection_id):
        section_id = ObjectId(section_id)
        subsection_id = ObjectId(subsection_id)
        
        # Удалите подраздел из раздела в базе данных
        db.sections.update_one(
            {"_id": section_id},
            {"$pull": {"subsections": {"_id": subsection_id}}}
        )
        
        return redirect(url_for("index"))


    # Удалите описания в подразделах 
    @app.route("/delete_description/<section_id>/<subsection_id>/<description_id>", methods=["POST"])
    def delete_description(section_id, subsection_id, description_id):
        section_id = ObjectId(section_id)
        subsection_id = ObjectId(subsection_id)
        description_id = ObjectId(description_id)  # Преобразуйте description_id в ObjectId
        
        # Удалите описание из подраздела в базе данных
        db.sections.update_one(
            {"_id": section_id, "subsections._id": subsection_id},
            {"$pull": {"subsections.$.descriptions": {"_id": description_id}}}
        )
        
        return redirect(url_for("index"))

    @app.route("/delete_rating/<section_id>/<subsection_id>/<description_id>/<rating_id>", methods=["POST"])
    def delete_rating(section_id, subsection_id, description_id, rating_id):
        section_id = ObjectId(section_id)
        subsection_id = ObjectId(subsection_id)
        description_id = ObjectId(description_id)
        rating_id = ObjectId(rating_id)
        
        db.sections.update_one(
            {"_id": section_id, "subsections._id": subsection_id, "subsections.descriptions._id": description_id},
            {"$pull": {"subsections.$.ratings": {"_id": rating_id}}}
        )
        
        return redirect(url_for("index"))




        #Редактирование имени раздела
    @app.route("/edit_section/<section_id>", methods=["POST"])
    def edit_section(section_id):
        new_section_name = request.form.get("new_section_name")
        db.sections.update_one({"_id": ObjectId(section_id)}, {"$set": {"name": new_section_name}})
        return redirect(url_for("index"))



        #Добавление характеристики
    @app.route("/add_characteristic/<section_id>/<subsection_id>", methods=["POST"])
    def add_characteristic(section_id, subsection_id):
        section_id = ObjectId(section_id)
        subsection_id = ObjectId(subsection_id)
        characteristic_text = request.form.get("characteristic")
        
        db.sections.update_one(
            {"_id": section_id, "subsections._id": subsection_id},
            {"$push": {"subsections.$.characteristics": characteristic_text}}
        )
        
        return redirect(url_for("index"))

    if __name__ == "__main__":
        app.run(debug=True)

    return app









