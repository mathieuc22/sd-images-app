from app import db


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(300), nullable=False)
    thumbnail = db.Column(db.String(300), nullable=False)
    parameters = db.Column(db.String(1000))
    negative_prompt = db.Column(db.String(500))
    steps = db.Column(db.Integer)
    sampler = db.Column(db.String(200))
    cfg_scale = db.Column(db.Float)
    seed = db.Column(db.BigInteger)
    size = db.Column(db.String(100))
    model_hash = db.Column(db.String(200))
    model = db.Column(db.String(200))
    liked = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Image {self.path}>"
