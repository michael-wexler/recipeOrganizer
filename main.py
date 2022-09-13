import setup
import utils
from recipe import Recipe
import recipe
import view

def main():
    cnn = setup.create_cnn(r"test_database")
    with cnn:
        #setup.create_tables(cnn)
        #setup.insert_table_values(cnn)
        ans = utils.get_user_input()
        if ans == 'insert':
            recipe_name = utils.get_recipe_name()
            recipe_notes = utils.get_recipe_notes()
            difficulty = utils.get_recipe_difficulty()
            cuisine = utils.get_recipe_cuisine()
            course = utils.get_recipe_course()
            diet = utils.get_recipe_diet()
            ingredients_dict = utils.get_recipe_ingredient()
            instructions = utils.get_recipe_instructions()
            newrecipe = Recipe(recipe_name, recipe_notes, ingredients_dict, difficulty, cuisine, course, diet, instructions)
            newrecipe.insert_all(cnn)
        if ans == 'view':
            criteria_dict = utils.get_search_criteria()
            recipes_df = view.print_recipes(cnn, **criteria_dict)
            print(view.ask_convert(recipes_df))
            return recipes_df

if __name__ == '__main__':
    main()