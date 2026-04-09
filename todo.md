# Todo

## ~~Blocs imbriqués~~ ✓

Permettre d'imbriquer des blocs les uns dans les autres.  
Lors de l'extraction d'un bloc parent, les lignes d'annotation enfants (`#XXX#BEGIN`, `#XXX#END`) sont supprimées du contenu généré.

```cpp
// #BUTTON_INIT#BEGIN
void initButton()
{
    // #BUTTON_BODY#BEGIN
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    // #BUTTON_BODY#END
}
// #BUTTON_INIT#END
```

---

## ~~`!INCLUDE` avec paramètres~~ ✓

Paramètres optionnels sur la directive `!INCLUDE`, ordre libre :

```markdown
!INCLUDE BLOCK_ID lang:html filename:true
```

- `lang:xxx` — override le langage du fenced block pour cet include
- `filename:true/false` — affiche ou masque le nom du fichier source, indépendamment du `include_filename` global du yaml
