# Todo

## Blocs imbriqués

Permettre d'imbriquer des blocs les uns dans les autres.  
Lors de l'extraction d'un bloc parent, les lignes d'annotation enfants (`#XXX#BEGIN`, `#XXX#END`) doivent être supprimées du contenu généré.

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

## `!INCLUDE` avec chemin explicite

Permettre de cibler un fichier précis dans la directive `!INCLUDE` :

```markdown
!INCLUDE led.cpp:LED_INIT
```

Utile quand `include_filename: false` est actif et qu'on veut quand même préciser l'origine d'un bloc, ou pour lever l'ambiguïté si un même nom de bloc existe dans plusieurs fichiers.
