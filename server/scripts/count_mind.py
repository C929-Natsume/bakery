# -*- coding: utf-8 -*-
from app_2 import create_app
from app_2.model.mind import MindKnowledge

def main():
    app = create_app()
    with app.app_context():
        c = MindKnowledge.query.count()
        print(f"mind_knowledge count={c}")
        rows = MindKnowledge.query.order_by(MindKnowledge.create_time.desc()).limit(5).all()
        for r in rows:
            print('-', r.id, r.title)

if __name__ == '__main__':
    main()
