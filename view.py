import pandas as pd

def print_recipes(cnn, **kwargs):
    sql = """SELECT recipe.recipe_id, recipe.recipe_name, recipe.recipe_notes,
                ingredient.ingredient, unit.unit, quantity.quantity, prepmethod.prepmethod,
                instructions.instructions, difficulty.difficulty, cuisine.cuisine,
                course.course, diet.diet
                FROM recipe_ingredient
                INNER JOIN recipe ON recipe.recipe_id = recipe_ingredient.recipe_id
                INNER JOIN ingredient ON ingredient.ingredient_id = recipe_ingredient.ingredient_id
                INNER JOIN unit ON unit.unit_id = recipe_ingredient.unit_id
                INNER JOIN quantity ON quantity.quantity_id = recipe_ingredient.quantity_id
                INNER JOIN prepmethod ON prepmethod.prepmethod_id = recipe_ingredient.prepmethod_id
                INNER JOIN instructions ON instructions.instruction_id = recipe.instructions_id
                INNER JOIN difficulty ON difficulty.difficulty_id = recipe.difficulty_id
                INNER JOIN cuisine ON cuisine.cuisine_id = recipe.cuisine_id
                INNER JOIN course ON course.course_id = recipe.course_id
                INNER JOIN diet ON diet.diet_id = recipe.diet_id
                """
    if len(kwargs) == 1:
        values = kwargs.popitem()
        if isinstance(values[1], str):
            sql2 = "WHERE {column} = '{selection}'".format(column=values[0], selection=values[1].lstrip())
        else:
            sql2 = "WHERE {column} = {selection}".format(column=values[0], selection=values[1])
        sql = sql + sql2
        count = 0
    if len(kwargs) > 1:
        li = []
        for key, value in kwargs.items():
            if isinstance(value, str):
                string = "{column} = '{selection}'".format(column=key, selection=value.lstrip())
            else:
                string = "{column} = {selection}".format(column=key, selection=value)
            li.append(string)
        count = 0
        toString = ""
        while count < len(li) - 1:
            toString = toString + li[count] + " OR "
            count = count + 1

        toString = toString + li[len(li) - 1]

        sql2 = "WHERE " + toString

        sql = sql + sql2

    recipe_df = pd.read_sql_query(sql, cnn)

    return recipe_df

def convert(recipes_df, conversion_unit):
    conversion_chart = {'tsp': 1 / 6,
                        'tbsp': 1 / 2,
                        'oz': 1,
                        'cup': 8,
                        'pint': 16,
                        'quart': 32,
                        'gallon': 128}
    to_convert = {}
    converted = {}
    repeat_ingredient = recipes_df.groupby('ingredient').nunique()["recipe_id"]
    for ingredient in repeat_ingredient[repeat_ingredient <= 1].iteritems():
        df = (recipes_df[recipes_df['ingredient'] == ingredient[0]])
        converted.update({ingredient[0] + " (" + df['unit'].iloc[0] + ")": df['quantity'].iloc[0]})
    ingredient_list = []
    for ingredient in repeat_ingredient[repeat_ingredient > 1].iteritems():
        ingredient_list.append(ingredient)
    for ingredient in ingredient_list:
        one_ingr_df = recipes_df[recipes_df['ingredient'] == ingredient[0]]
        total_floz = 0
        for unit in one_ingr_df['unit'].unique():
            if unit in conversion_chart:
                unit_sum = pd.to_numeric(one_ingr_df[one_ingr_df['unit'] == unit]['quantity']).sum()
                floz = unit_sum * conversion_chart[unit]
                total_floz = total_floz + floz
                to_convert.update({ingredient[0]: total_floz})
            else:
                unit_sum = pd.to_numeric(
                    one_ingr_df[one_ingr_df['unit'] == unit]['quantity']).sum()
                converted.update({"summed " + ingredient[0] + " (" + unit + ")": unit_sum})
    for ingredient in to_convert:
        converted.update(
            {("summed " + ingredient + " (" + conversion_unit + ")"): to_convert[ingredient] / conversion_chart[conversion_unit]})
    return (converted)

def ask_convert(recipes_df):
    while True:
        answer = input("Would you like to aggregate your ingredients? Enter 'yes' or 'no'.")
        if answer not in ('yes', 'no'):
            print("Please enter a valid answer.")
            continue
        else:
            break
    if answer == 'no':
        print("See ingredients in table of recipes.")
    else:
        while True:
            conversion_unit = input("Please choose a unit for your aggregated ingredients (tsp, tbsp, oz, cup, pint, quart, gallon).")
            if conversion_unit not in ('tsp', 'tbsp', 'oz', 'cup', 'pint', 'quart', 'gallon'):
                print("Please enter a valid answer.")
                continue
            else:
                break
        return convert(recipes_df, conversion_unit)
