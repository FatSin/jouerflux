# blablaaaaaaaaaa

from typing import Dict, List
from app import db
from models import Rule, Policy, Host
from exceptions import DatabaseError, IntegrityError, NotFoundInDB, GenericError


class RuleContext:
    def __init__(self):
        # init session
        self.session = db.session

    def get_rule(self, rule_uuid: int) -> Dict:
        if rule_uuid:
            try:
                rule = Rule.query.filter_by(rule_uuid=rule_uuid).first()
                res = rule.as_dict() if rule else rule
            except Exception as e:
                raise DatabaseError(f"Couldn't read from DB {e}")
            if not res:
                raise NotFoundInDB(rule_uuid)
            return res
        else:
            raise GenericError(f" Function received no uuid")

    def get_policy_rules(self, pol_uuid: str) -> List[Dict]:
        try:
            policy = Policy.query.filter_by(policy_uuid=pol_uuid).first()
            res = policy.as_dict()["rules"]
            return res
        except Exception as e:
            raise DatabaseError(f"Counldn't fetch policies from the DB. {e}")

    def add_policy_rule(self, pol_uuid: str, rule: dict):

        pol_uuid = pol_uuid
        rule_uuid = rule.get("uuid", None)
        action = rule.get("action", None)
        src_uuid = rule.get("source", None)
        dst_uuid = rule.get("destination", None)
        service = rule.get("service", None)

        if Rule.query.filter_by(rule_uuid=rule_uuid).first():
            raise IntegrityError(rule_uuid)

        try:
            # get policy by id
            policy = Policy.query.filter_by(policy_uuid=pol_uuid).first()
            source = Host.query.filter_by(host_uuid=src_uuid).first()
            dest = Host.query.filter_by(host_uuid=dst_uuid).first()
        except Exception as e:
            raise DatabaseError(f"Couldn't read from DB {e}")
        if not all((policy, source, dest)):
            raise NotFoundInDB(f"Policy, source or destination not found in DB.")

        try:
            # Auto-increment the IDs
            rules = Rule.query.all()
            rules_ids = sorted([rule.rule_id for rule in rules])
            new_id = rules_ids[-1] + 1 if rules_ids else 1
            rule = Rule(rule_id=new_id,
                            rule_uuid=rule_uuid,
                            action=action,
                            service=service,
                            fk_source=source.host_id,
                            fk_dest=dest.host_id,
                            fk_policy=policy.policy_id)

            self.session.add(rule)
            self.session.commit()
            return 'Succeeded', 201
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Couldn't add Rule with uuid {rule_uuid}"
                                f" to policy {pol_uuid}. {e}")


    def update_rule(self, rule: dict):

        rule_uuid = rule.get("uuid", None)
        action = rule.get("action", None)
        src_uuid = rule.get("source", None)
        dst_uuid = rule.get("destination", None)
        service = rule.get("service", None)

        if not rule_uuid:
            raise GenericError("No rule uuid given.")
        if not all((action, src_uuid, dst_uuid)):
            raise GenericError("Missing fields. Action, source an destination"
                               " UUID must be given.")

        try:
            rule = Rule.query.filter_by(rule_uuid=rule_uuid).first()
        except Exception as e:
            raise DatabaseError(f"Couldn't get Rule with uuid {rule_uuid}. {e}")

        try:
            source = Host.query.filter_by(host_uuid=src_uuid).first()
            dest = Host.query.filter_by(host_uuid=src_uuid).first()
        except Exception as e:
            raise DatabaseError(f"Couldn't read from DB. {e}")

        if not rule:
            raise NotFoundInDB(rule_uuid)
        elif not all((source, dest)):
            raise NotFoundInDB(f"{src_uuid} or {dst_uuid}")

        try:
            rule.action = action
            rule.service = service
            rule.fk_source = source.host_id
            rule.fk_dest = dest.host_id

            self.session.commit()

        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Couldn't update Rule with uuid {rule}. {e}")

    def delete_rule(self, rule_uuid):
        try:
            rule = Rule.query.filter_by(rule_uuid=rule_uuid).first()
        except Exception as e:
            raise DatabaseError(f"Couldn't delete Rule with uuid {rule_uuid}. {e}")

        if not rule:
            raise NotFoundInDB(rule_uuid)

        try:
            self.session.delete(rule)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Couldn't delete Rule with uuid {rule_uuid}. {e}")


rule_context = RuleContext()


def get_policy_rules(uuid):
    return rule_context.get_policy_rules(uuid)


def get_rule(uuid):
    return rule_context.get_rule(uuid)


def delete_rule(uuid):
    return rule_context.delete_rule(uuid)


def add_policy_rule(uuid: str, rule: dict):
    return rule_context.add_policy_rule(uuid, rule)


def update_rule(rule: dict):
    return rule_context.update_rule(rule)