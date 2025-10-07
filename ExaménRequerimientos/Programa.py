import json

CONTACTS_FILE = "contacts.json"

def load_contacts():
    try:
        with open(CONTACTS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_contacts(contacts):
    with open(CONTACTS_FILE, "w") as f:
        json.dump(contacts, f, indent=4)

def registrar_contacto():
    nombre = input("Nombre: ")
    correo = input("Correo: ")
    telefono = input("Teléfono: ")
    cargo = input("Cargo: ")
    contactos = load_contacts()
    contactos.append({
        "nombre": nombre,
        "correo": correo,
        "telefono": telefono,
        "cargo": cargo
    })
    save_contacts(contactos)
    print("Contacto registrado.")

def buscar_contacto():
    criterio = input("Buscar por (nombre/correo/telefono/cargo): ").lower()
    valor = input(f"Ingrese el {criterio}: ")
    contactos = load_contacts()
    encontrados = [c for c in contactos if c.get(criterio, "").lower() == valor.lower()]
    if encontrados:
        for c in encontrados:
            print(c)
    else:
        print("No se encontró el contacto.")

def eliminar_contacto():
    nombre = input("Nombre del contacto a eliminar: ")
    contactos = load_contacts()
    nuevos_contactos = [c for c in contactos if c["nombre"].lower() != nombre.lower()]
    if len(contactos) == len(nuevos_contactos):
        print("Contacto no encontrado.")
    else:
        save_contacts(nuevos_contactos)
        print("Contacto eliminado.")

def menu():
    while True:
        print("\n1. Registrar contacto")
        print("2. Buscar contacto")
        print("3. Eliminar contacto")
        print("4. Salir")
        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            registrar_contacto()
        elif opcion == "2":
            buscar_contacto()
        elif opcion == "3":
            eliminar_contacto()
        elif opcion == "4":
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu()