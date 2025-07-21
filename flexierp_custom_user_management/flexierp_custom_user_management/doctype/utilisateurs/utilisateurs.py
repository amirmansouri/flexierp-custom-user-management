import frappe
from frappe.model.document import Document
import string
import random
from frappe import _

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

    if isinstance(doc.role, str):
        user.append("roles", {"role": doc.role})
    elif isinstance(doc.role, list):
        for role in doc.role:
            user.append("roles", {"role": role})

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
        utilisateur.save(ignore_permissions=True)

         


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




 

