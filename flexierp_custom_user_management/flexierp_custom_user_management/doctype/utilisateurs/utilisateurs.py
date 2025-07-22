import frappe
from frappe.model.document import Document
import string
import random
from frappe import _
from urllib.parse import unquote


class Utilisateurs(Document):
    def on_submit(self):
        create_or_update_user(self)



def create_or_update_user(doc, method=None):
    if not doc.email:
        frappe.throw(_("L'adresse email est obligatoire."))

        frappe.logger().info(f"Création/mise à jour de l'utilisateur pour {doc.email}")


    if frappe.db.exists("User", {"email": doc.email}):
        user = frappe.get_doc("User", {"email": doc.email})
        frappe.msgprint(_("Mise à jour de l'utilisateur existant."))
    else:
        user = frappe.new_doc("User")
        user.email = doc.email
        user.enabled = 1
        user.send_welcome_email = 0
        frappe.msgprint(_("Création d'un nouvel utilisateur."))

    user.first_name = doc.full_name or doc.email
    user.phone = doc.telephone
    user.user_type = "System User"

    if doc.password:
        user.new_password = doc.password

    user.set("roles", [])

     
    role_value = unquote(doc.role) if isinstance(doc.role, str) else None

     
    if role_value and frappe.db.exists("Role", {"name": role_value}):
        user.append("roles", {"role": role_value})
    else:
        frappe.throw(_("Le rôle spécifié est invalide ou introuvable: {0}").format(role_value))

    user.save(ignore_permissions=True)

    frappe.db.set_value("Utilisateurs", doc.name, "user_id", user.name)
   
    frappe.msgprint(_("Utilisateur synchronisé avec succès : {0}").format(user.name))



@frappe.whitelist()
def sync_utilisateur_on_password_change(doc, method):


    if not doc.email or not doc.new_password:
        return

    if frappe.db.exists("Utilisateurs", {"email": doc.email}):
        utilisateur = frappe.get_doc("Utilisateurs", {"email": doc.email})
        utilisateur.password = doc.new_password
        utilisateur.save(ignore_permissions=True, ignore_mandatory=True)

        

         


@frappe.whitelist()
def generate_password(email):


    if not email:
        frappe.throw(_("Aucun email fourni"))

    if not frappe.db.exists("User", {"email": email}):
        frappe.throw(_("Aucun utilisateur trouvé avec l'email : {0}").format(email))

    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(random.choice(characters) for _ in range(15))

    user_doc = frappe.get_doc("User", {"email": email})
    user_doc.new_password = password
    user_doc.save(ignore_permissions=True)

    if frappe.db.exists("Utilisateurs", {"email": email}):
        utilisateur = frappe.get_doc("Utilisateurs", {"email": email})
        utilisateur.password = password
        utilisateur.save(ignore_permissions=True)
    frappe.msgprint(_("Le nouveau mot de passe est: {0}").format(password))
    return _("Le nouveau mot de passe est: {0}").format(password)

@frappe.whitelist()
def get_roles_by_company(doctype, txt, searchfield, start, page_len, filters):
    """
    Return roles from 'Roles Visibility Management' for the selected company.
    Used to filter role dropdown in Utilisateurs doctype.
    """
    company = filters.get("company")
    if not company:
        return []

    # Get records in Roles Visibility Management for that company
    rvm_names = frappe.get_all(
        "Roles Visibility Management",
        filters={"company": company},
        pluck="name"
    )

    if not rvm_names:
        return []

    # Get Role entries from the child table Role Entry
    roles = frappe.get_all(
        "Role Entry",
        filters={"parent": ["in", rvm_names]},
        fields=["role"]
    )

    return [(r["role"],) for r in roles]



 

