# link
https://experience.adobe.com/#/@eneldhcom/experiencemanager/

  # Step 1: Sync feature branch with master
  git checkout brunello/feature/dr-calculator-vue
  git merge origin/master

  # Step 2: Merge into develop
  git checkout develop
  git pull origin develop
  git merge brunello/feature/dr-calculator-vue
  git push origin develop

  git checkout develop
  git pull origin develop
  git submodule update --remote institutionals--north-america
  git add institutionals--north-america
  git commit -m "Update institutionals--north-america submodule for DR Calculator Vue"
  git push origin develop
