from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


class MyApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data = {}
        self.add_url_rule('/', view_func=self.index, methods=['GET', 'POST'])
        self.add_url_rule('/submitFirstPage',
                          view_func=self.submitFirstPage, methods=['POST'])
        self.add_url_rule('/page2', view_func=self.page2)
        self.add_url_rule('/submit', view_func=self.submit, methods=['POST'])

    def index(self):
        return render_template('Page1.html')

    def submitFirstPage(self):
        self.data = dict(request.form)
        return redirect(url_for('page2'))

    def page2(self):
        print(self.data)
        return render_template('Page2.html')

    def submit(self):
        print(request.form)
        print(request.files)
        return '<h1>Submitted, please wait</h1>'


app = MyApp(__name__)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
