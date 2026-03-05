import numpy as np

def cos_np(v1,v2):
   """
   Calcule la similarité consinus entre deux vecteurs

   Arguments :
        v1 (np.ndarray) : le premier vecteur 
        v2 (np.ndarray) : le deuxième vecteur 
   Return : 
        float : le score de simimarité cosinus (entre 0 et 1). 
                Retourne 0 si l'un des deux vecteurs est nul
   """
   produit = np.dot(v1,v2)
   norme1 = np.linalg.norm(v1)
   norme2 = np.linalg.norm(v2)

   if norme1 * norme2 !=0:
      return produit / (norme1 * norme2)
   return 0

def jaccard_np(v1,v2):
   """
   Calcule l'indice de Jaccard entre deux vecteurs.

   Arguments : 
        v1 (np.ndarray) : le premier vecteur 
        v2 (np.ndarray) : le deuxième vecteur 
    Return : 
        float : l'indice de Jaccard
   """
   p1 = v1>0
   p2 = v2>0

   inter = np.sum(p1 & p2)
   union = np.sum(p1 | p2)

   if union !=0:
      return inter / union
   return 0
