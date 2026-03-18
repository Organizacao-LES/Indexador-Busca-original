import postgresql_driver as pgd

def inserirUsuario():
    query= "SELECT *"
    
    res = pgd.executar(query)
    return res