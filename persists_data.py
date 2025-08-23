from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["scrapedpublications"]      
collection = db["publications"]         

def save_to_db(link):
    collection.insert_one({
            "link": link
    })
    print("Saved to DB:", link)

def get_links_from_db():
    return [doc["link"] for doc in collection.find({}, {"link": 1})]

def update_to_db(detail):
    collection.update_one(
        {"link": detail.get("link"), "title": {"$exists": False}},
        {
            "$set": {
                "title": detail.get("title"),
                "abstract": detail.get("abstract"),
                "language": detail.get("language"),
                 "published": detail.get("published"),
                 "authors": detail.get("authors")
        }
    })