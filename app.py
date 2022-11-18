from sqlalchemy import Column, Integer, String, DateTime, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from flask import Flask, request, jsonify
from flask.views import MethodView

app = Flask('Adv')

DSN = 'postgresql://app:1234@db:5432/data'
engine = create_engine(DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Advertisement(Base):
    __tablename__ = "advertisement"

    id = Column(Integer, primary_key=True)
    header = Column(String(32), nullable=False)
    description = Column(String(32), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    owner = Column(Integer, nullable=False)


Base.metadata.create_all(engine)


class AdvertisementView(MethodView):
    def get(self, adv_id=''):
        with Session() as session:
            if adv_id:
                advertisement = session.query(Advertisement).get(adv_id)
                if advertisement:
                    answer = {
                        'id': advertisement.id,
                        'header': advertisement.header,
                        'description': advertisement.description,
                        'created_at': advertisement.created_at,
                        'owner': advertisement.owner
                    }
                else:
                    answer = {
                        'status': 404,
                        'message': 'advertisement not found'
                        }
            else:
                advertisements = session.query(Advertisement).all()
                answer = {}
                if advertisements:
                    for num, adv in enumerate(advertisements):
                        answer[f'{num}'] = {
                            'id': adv.id,
                            'header': adv.header,
                            'description': adv.description,
                            'created_at': adv.created_at,
                            'owner': adv.owner
                        }
                answer = {
                    'response': {'count': len(advertisements), 'items': answer}
                }
            return jsonify(answer)

    def post(self):
        load_data = request.json
        with Session() as session:
            new_adv = Advertisement(**load_data)
            session.add(new_adv)
            session.commit()
            return jsonify({'cereated advertisement': load_data})

    def patch(self, adv_id):
        updated_data = request.json
        with Session() as session:
            adv = session.query(Advertisement).filter_by(id=adv_id)
            if adv.count():
                adv.update(updated_data)
                session.commit()
                return jsonify({'status': "updated"})
            else:
                answer = {
                    'status': 404,
                    'message': 'advertisement not found'
                }
                return jsonify(answer)

    def delete(self, adv_id):
        with Session() as session:
            adv = session.query(Advertisement).get(adv_id)
            if adv:
                session.delete(adv)
                session.commit()
                return jsonify({'status': 'deleted'})
            else:
                answer = {
                    'status': 404,
                    'message': 'advertisement not found'
                }
                return jsonify(answer)


app.add_url_rule(
    "/api/v1/adv/<int:adv_id>/", view_func=AdvertisementView.as_view("get_adv"), methods=["GET", "PATCH", "DELETE"]
)
app.add_url_rule(
    "/api/v1/adv/", view_func=AdvertisementView.as_view("register_adv"), methods=["GET", "POST"]
)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
