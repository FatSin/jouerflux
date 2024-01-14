# blablaaaaaaaaaaa

from enum import Enum

# from flask import current_app
# from flask_sqlalchemy import SQLAlchemy
from app import db, flask_app

# db = SQLAlchemy(flask_app)

class OperStatus(Enum):
    active = "active"
    inactive = "inactive"
    error = "error"


class BillingStatus(Enum):
    active = "active"
    decommissioned = "decommissioned"


class ClusterStatus(Enum):
    ha = "ha"
    standalone = "standalone"


class ActionRule(Enum):
    accept = 'accept'
    deny = 'deny'
    inspect = 'inspect'


class Firewall(db.Model):
    __tablename__ = 'firewall'
    __table_args__ = {'extend_existing': True}
    firewall_id = db.Column(db.Integer, primary_key=True)
    firewall_uuid = db.Column(db.String(50), unique=True, nullable=False)
    hostname = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    fk_manager = db.Column(db.Integer, db.ForeignKey('manager.manager_id'))
    zone = db.Column(db.String(50), nullable=False)
    billing_status = db.Column(db.Enum(BillingStatus), nullable=False)
    oper_status = db.Column(db.Enum(OperStatus), nullable=False)
    fk_policy = db.Column(db.Integer, db.ForeignKey('policy.policy_id'))
    cluster_status = db.Column(db.Enum(ClusterStatus), nullable=False)
    fk_cluster = db.Column(db.Integer, db.ForeignKey('cluster.cluster_id'))

    def as_dict(self):
        return { "uuid": self.firewall_uuid,
                 "hostname": self.hostname,
                 "ipAddress": self.ip_address,
                 "manager": "",
                 "zone": self.zone,
                 "operStatus": self.oper_status._value_,
                 "billingStatus": self.billing_status._value_,
                 "clusterInfo": self.cluster_status._value_
                 }


# On voit bien qu'il y a de la refacto possible pour merger les 2 types de node (firewalls et managers)
# Par exemple, on peut ajouter un booléen 'manager' à la classe Firewall, ainsi gateways et managers
# seront de type Firewall
class Manager(db.Model):
    __tablename__ = 'manager'
    __table_args__ = {'extend_existing': True}
    manager_id = db.Column(db.Integer, primary_key=True)
    manager_uuid = db.Column(db.String(50), unique=True, nullable=False)
    hostname = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    billing_status = db.Column(db.Enum(BillingStatus), nullable=False)
    oper_status = db.Column(db.Enum(OperStatus), nullable=False)
    cluster_status = db.Column(db.Enum(ClusterStatus), nullable=False)
    fk_cluster = db.Column(db.Integer, db.ForeignKey('cluster.cluster_id'))


class Cluster(db.Model):
    __tablename__ = 'cluster'
    __table_args__ = {'extend_existing': True}
    cluster_id = db.Column(db.Integer, primary_key=True)
    cluster_name = db.Column(db.String(50), nullable=False)
    cluster_ip = db.Column(db.String(15), nullable=False)


class Policy(db.Model):
    __tablename__ = 'policy'
    __table_args__ = {'extend_existing': True}
    policy_id = db.Column(db.Integer, primary_key=True)
    policy_uuid = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    last_modification_date = db.Column(db.DateTime, nullable=False)
    version = db.Column(db.Integer, nullable=False)
    firewalls = db.relationship('Firewall',
                               backref=db.backref('firewalls'))
    rules = db.relationship('Rule',
                               backref=db.backref('rules'))

    def as_dict(self):
        return { "uuid": self.policy_uuid,
                 "name": self.name,
                 "lastModificationDate": self.last_modification_date,
                 "version": self.version,
                 "deployedOn": [ fw.as_dict() for fw in self.firewalls],
                 "rules" : [ rule.as_dict() for rule in self.rules]
                 }

# Si on veut basculer en many to many (ie plusieurs policies par firewall), on peut
# supprimer la fk policy de la classe Firewall et passer par une table intermédiaire, comme ceci :

# class PolicyPush(db.Model):
#     __tablename__ = 'policy_push'
#     __table_args__ = {'extend_existing': True}
#     push_id = db.Column(db.Integer, primary_key=True)
#     push_date = db.Column(db.DateTime, nullable=False)
#     fk_firewall = db.Column(db.Integer, db.ForeignKey('firewall.firewall_id'))
#     fk_policy = db.Column(db.Integer, db.ForeignKey('policy.policy_id'))

# Il faudra alors reconfigurer les specs en conséquence


class Rule(db.Model):
    __tablename__ = 'rule'
    __table_args__ = {'extend_existing': True}
    rule_id = db.Column(db.Integer, primary_key=True)
    rule_uuid = db.Column(db.String(50), unique=True, nullable=False)
    action = db.Column(db.Enum(ActionRule), nullable=False)
    service = db.Column(db.String(50), unique=True, nullable=False)
    fk_source = db.Column(db.Integer, db.ForeignKey('host.host_id'))
    fk_dest = db.Column(db.Integer, db.ForeignKey('host.host_id'))
    fk_policy = db.Column(db.Integer, db.ForeignKey('policy.policy_id'))
    source = db.relationship('Host', foreign_keys=[fk_source])
    dest = db.relationship('Host', foreign_keys=[fk_dest])

    def as_dict(self):
        return { "uuid": self.rule_uuid,
                 "action": self.action._value_,
                 "source": self.source.as_dict(),
                 "destination": self.dest.as_dict(),
                 "service": self.service
                 }


class Host(db.Model):
    __tablename__ = 'host'
    __table_args__ = {'extend_existing': True}
    host_id = db.Column(db.Integer, primary_key=True)
    host_uuid = db.Column(db.String(50), unique=True, nullable=False)
    subnet = db.Column(db.String(15), nullable=False)
    mask = db.Column(db.String(15), nullable=False)
    # Pour simplifier, hosts et subnets sont de même type et on joue sur le subnet mask

    def as_dict(self):
        return {"uuid": self.host_uuid,
                "ipAddress": self.subnet,
                "mask": self.mask
                }

import os
if os.environ.get('INIT_DB', None):
   print('Init db...')
   with flask_app.app_context():
       try:
            db.drop_all()
            db.create_all()
            host1 = Host(host_id = 1,
                            host_uuid = "100e4567-e89b-12d3-a456-426655440010",
                            subnet = "10.0.0.10",
                            mask = "255.255.255.255"
            )
            host2 = Host(host_id=2,
                         host_uuid="200e4567-e89b-12d3-a456-426655440020",
                         subnet="192.168.1.20",
                         mask="255.255.255.255"
                         )
            db.session.add_all([host1, host2])
            db.session.commit()
       except Exception as e:
           print('failed')
           print(e)
       print('...DB initiated')
