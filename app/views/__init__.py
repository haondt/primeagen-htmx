from flask import Flask, render_template, request
from typing import Any as trust
import time

class FalsyAny:
    def __bool__(self):
        return False
    def __getattr__(self, name):
        return self
    def __setattr__(self, name, value):
        pass

class Anon:
    def __init__(self, d={}):
        self._anon_contents = d
    def __getattr__(self, name) -> trust:
        if name in self._anon_contents:
            return self._anon_contents.get(name)
        return FalsyAny()
    def __setattr__(self, name, value):
        if name.startswith("_"):
            self.__dict__[name] = value
        else:
            self._anon_contents[name] = value

def init_state():
    next_contact_id = 0
    def add_contact(s, name, email):
        contact = Anon({'name': name, 'email': email})
        nonlocal next_contact_id
        contact.id = next_contact_id
        next_contact_id += 1
        s.contacts.append(contact)
        return contact
    def index_of(s, id: int) -> int:
        for i, c in enumerate(s.contacts):
            if c.id == id:
                return i
        return -1

    state = Anon()
    state.contacts = []
    state.add_contact = lambda n, e: add_contact(state, n, e)
    state.index_of = lambda i: index_of(state, i)

    state.add_contact("John", "jd@gmail.com")
    state.add_contact("Clara", "cd@gmail.com")

    state.has_email = lambda e: any([e == c.email for c in state.contacts])
    state.formdata = Anon({'values': Anon(), 'errors': Anon()})

    return state


def apply(site):
    state = init_state()

    @site.route('/', methods=['GET'])
    def home():
        return render_template('index.html', d=state)

    @site.route('/contacts', methods=['POST'])
    def add_contact():
        name = request.form['name']
        email = request.form['email']
        
        if state.has_email(email):
            formdata = Anon({'values': Anon(), 'errors': Anon()})
            formdata.values.name = name
            formdata.values.email = email
            formdata.errors.email = 'Email already exists'

            return render_template('form.html', d=Anon({'formdata': formdata})), 422
        
        contact = state.add_contact(name, email)
        return render_template('form.html', d=Anon()) + \
            render_template('oob-contact.html', contact=contact)

    @site.route('/contacts/<id>', methods=['DELETE'])
    def delete_contact(id):
        time.sleep(3)
        id = int(id)
        index = state.index_of(id)
        if index < 0:
            return "Contact not found", 404
        state.contacts = state.contacts[:index] + state.contacts[index + 1:]

        return '', 200

