import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
connection_string = 'postgres://ntfojjjyonvtro:74e073640678f970e8512871d60eaff786cbafa7dc5799f8bb70a36faa985456@ec2-54-235-158-17.compute-1.amazonaws.com:5432/dbkgnqld1e0ai0'

engine = create_engine(connection_string)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
# quotes = Base.classes.quotes
# authors = Base.classes.author
# tags = Base.classes.tags

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/quotes<br/>"
        f"/top10tags"
    )


@app.route("/quotes")
def quotes():
    result = {}
    data = engine.execute('''select id, 
    author_name,
    text
    from quotes q 
    inner join author a on q.author_name = a.name
    order by id''')
    total_quotes = data.rowcount
    result['total'] = total_quotes

    quotes = []
    for row in data:
        quote = {}
        quote['text'] = row.text.replace('\u201c','').replace('\u201d','').replace('\u2019',"'").replace('\u2032',"'").replace('\u2014','--')
        quote['author'] = row.author_name.replace('\u00e9','e')
        tags = []
        tags_result = engine.execute(
            f'select tag  from tags where quote_id= {row.id}')
        for tagrow in tags_result:
            tags.append(tagrow.tag)
        quote['tags'] = tags
        quotes.append(quote)

    result['quotes'] = quotes
    return jsonify(result)

@app.route("/top10tags")
def top10tags():
    result = []
    tags_data = engine.execute('''select tag , 
    count(*) as total 
    from tags
    group by tag
    order by total desc
    limit 10''')
    for row in tags_data:
        tag = {}
        tag['tag'] = row.tag
        tag['total'] = row.total
        result.append(tag)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)

