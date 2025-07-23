import {expect, test} from '@playwright/test';
import {pizzas} from '../api-responses';

test.describe('Render', () => {
  test.beforeEach(async ({page}) => {
    await page.route('*/**/api/v1/resource/product?type=pizza&pageNumber=0&pageSize=7', async route => {
      await route.fulfill({json: pizzas});
    });

    await page.goto('/pizzas');

    const openCustomPizza = page.getByTitle('Open Custom Pizza Builder').getByRole(`button`);
    await openCustomPizza.click();
  });

  test('ShowHeader', async ({page}) => {
    await expect(page.getByLabel('Personalize however you like!').getByText('Personalize however you like!')).toBeVisible();
  });

  test('ShowTheEssentials', async ({page}) => {
    await expect(page.getByText('The Essentials')).toBeVisible();

    await expect(page.getByText('Size')).toBeVisible();
    await expect(page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Medium'})).toBeVisible();
    await expect(page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Large'})).toBeVisible();
    await expect(page.getByText('Allergens').first()).toBeVisible();
    await expect(page.getByRole('button', {name: 'Gluten free'})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Gluten free'})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Lactose free'})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Lactose free'})).toBeDisabled();
    await expect(page.getByText('Base sauce layer')).toBeVisible();
    await expect(page.getByRole('button', {name: 'Tomato Sauce'})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Tomato Sauce'})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Cream Sauce'})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Cream Sauce'})).toBeDisabled();
    await expect(page.getByText('Base cheese layer', {exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: '100% Mozzarella', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: '100% Mozzarella', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Double 100% Mozzarella'})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Double 100% Mozzarella'})).toBeDisabled();
  });

  test('ShowIngredients', async ({page}) => {
    await expect(page.getByText('Ingredients')).toBeVisible();

    await expect(page.getByText('Meat')).toBeVisible();

    await expect(page.getByRole('button', {name: 'Smoked Bacon', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Smoked Bacon', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Double Smoked Bacon'})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Double Smoked Bacon'})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Pepperoni', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Pepperoni', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Double Pepperoni', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Double Pepperoni', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Beef', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Beef', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'York Ham', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'York Ham', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Chicken', exact: true})).toBeDisabled();

    await expect(page.getByText('Cheese', {exact: true})).toBeVisible();

    await expect(page.getByRole('button', {name: 'Parmesan Cheese', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Parmesan Cheese', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Emmental Cheese'})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Emmental Cheese'})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Goat Cheese', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Goat Cheese', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Blue Cheese', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Blue Cheese', exact: true})).toBeDisabled();

    await expect(page.getByText('Vegetable')).toBeVisible();

    await expect(page.getByRole('button', {name: 'Zucchini', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Zucchini', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Sliced Tomato'})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Sliced Tomato'})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Onion', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Onion', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Mushroom', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Mushroom', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Eggplant', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Eggplant', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Black Olives', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Black Olives', exact: true})).toBeDisabled();

    await expect(page.getByText('Oil', {exact: true})).toBeVisible();

    await expect(page.getByRole('button', {name: 'White Truffle Oil', exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: 'White Truffle Oil', exact: true})).toBeDisabled();
  });

  test('ShowAllergens', async ({page}) => {
    await expect(page.getByTitle('Allergens').getByText('Allergens')).toBeVisible();
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
  });

  test('ShowActionButtons', async ({page}) => {
    await expect(page.getByRole('button', {name: 'RESET'})).toBeVisible();
    await expect(page.getByLabel('Personalize however you like!').getByRole('button', {name: 'ADD'})).toBeVisible();
    await expect(page.getByLabel('Personalize however you like!').getByRole('button', { name: 'ADD' })).toBeDisabled();
  });

  test('ShowInformativeButtons', async ({page}) => {
    await expect(page.getByRole('button', {name: '0.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();
  });

  test('givenMediumSizeSelect_thenEnableButtons', async ({page}) => {

    // Arrange

    const medium = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Medium'});

    // Act

    await medium.click();

    // Assert

    await expect(medium).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: 'Gluten free'})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Lactose free'})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Tomato Sauce'})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Cream Sauce'})).toBeEnabled();
    await expect(page.getByRole('button', {name: '100% Mozzarella', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Double 100% Mozzarella'})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Smoked Bacon', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Double Smoked Bacon'})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Double Pepperoni', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Pepperoni', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Beef', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'York Ham', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Chicken', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Parmesan Cheese', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Emmental Cheese'})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Goat Cheese', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Blue Cheese', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Zucchini', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Sliced Tomato'})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Onion', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Mushroom', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Eggplant', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Black Olives', exact: true})).toBeEnabled();
  });
});

test.describe('Format', () => {
  test.beforeEach(async ({page}) => {
    await page.route('*/**/api/v1/resource/product?type=pizza&pageNumber=0&pageSize=7', async route => {
      await route.fulfill({json: pizzas});
    });

    await page.goto('/pizzas');

    const openCustomPizza = page.getByTitle('Open Custom Pizza Builder').getByRole(`button`);
    await openCustomPizza.click();
  });

  test('givenLargeSizeSelect_whenMediumAndLactoseFreeAndGlutenFreeAndIngredient_thenReset', async ({page}) => {

    // Arrange

    const medium = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Medium'});
    const large = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Large'});
    const glutenFree = page.getByRole('button', {name: 'Gluten free'});
    const lactoseFree = page.getByRole('button', {name: 'Lactose free'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce'});
    const bacon = page.getByRole('button', {name: 'Smoked Bacon', exact: true});
    await medium.click();

    // Act

    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(medium).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();

    await glutenFree.click();
    await expect(page.getByText('Gluten', {exact: true})).not.toBeVisible();
    await expect(glutenFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '13.00€'})).toBeVisible();

    await lactoseFree.click();
    await expect(lactoseFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '15.00€'})).toBeVisible();

    await creamSauce.click();
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '15.00€'})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await bacon.click();
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '16.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await large.click();
    await expect(large).toHaveCSS('color', 'rgb(249, 115, 22)');

    // Assert

    await expect(page.getByRole('button', {name: '14.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(medium).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(glutenFree).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(lactoseFree).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(creamSauce).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(bacon).not.toHaveCSS('color', 'rgb(249, 115, 22)');
  });

  test('givenMediumSizeSelect_whenLargeAndLactoseFreeAndGlutenFreeAndIngredient_thenReset', async ({page}) => {

    // Arrange

    const medium = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Medium'});
    const large = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Large'});
    const glutenFree = page.getByRole('button', {name: 'Gluten free'});
    const lactoseFree = page.getByRole('button', {name: 'Lactose free'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce'});
    const mozzarella = page.getByRole('button', {name: '100% Mozzarella', exact: true});
    const bacon = page.getByRole('button', {name: 'Smoked Bacon', exact: true});
    await large.click();

    // Act

    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(large).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '14.00€'})).toBeVisible();

    await glutenFree.click();
    await expect(page.getByText('Gluten', {exact: true})).not.toBeVisible();
    await expect(glutenFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '18.00€'})).toBeVisible();

    await lactoseFree.click();
    await expect(lactoseFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '22.00€'})).toBeVisible();

    await creamSauce.click();
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '22.00€'})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await bacon.click();
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '24.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await mozzarella.click();
    await expect(mozzarella).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '24.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3/9'})).toBeVisible();

    await medium.click();
    await expect(medium).toHaveCSS('color', 'rgb(249, 115, 22)');

    // Assert

    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(large).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(glutenFree).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(lactoseFree).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(creamSauce).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(bacon).not.toHaveCSS('color', 'rgb(249, 115, 22)');
  });
});

test.describe('Gluten Free', () => {
  test.beforeEach(async ({page}) => {
    await page.route('*/**/api/v1/resource/product?type=pizza&pageNumber=0&pageSize=7', async route => {
      await route.fulfill({json: pizzas});
    });

    await page.goto('/pizzas');

    const openCustomPizza = page.getByTitle('Open Custom Pizza Builder').getByRole(`button`);
    await openCustomPizza.click();
  });

  test('givenGlutenFreeClick_whenNotGlutenFree_thenRemoveGlutenAllergenAndUpdatePrice', async ({page}) => {

    // Arrange

    const medium = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Medium'});
    const glutenFree = page.getByRole('button', {name: 'Gluten free'});
    const tomatoSauce = page.getByRole('button', {name: 'Tomato Sauce', exact: true});
    const bacon = page.getByRole('button', {name: 'Smoked Bacon', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act

    await medium.click();
    await expect(medium).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();

    await tomatoSauce.click();
    await expect(tomatoSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await bacon.click();
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '12.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await glutenFree.click();

    // Assert

    await expect(glutenFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '14.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();
    await expect(page.getByText('Gluten', {exact: true})).not.toBeVisible();
  });

  test('givenGlutenFreeClick_whenGlutenFree_thenAddGlutenAllergenAndUpdatePrice', async ({page}) => {

    // Arrange

    const medium = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Medium'});
    const glutenFree = page.getByRole('button', {name: 'Gluten free'});
    const tomatoSauce = page.getByRole('button', {name: 'Tomato Sauce', exact: true});
    const bacon = page.getByRole('button', {name: 'Smoked Bacon', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act

    await medium.click();
    await expect(medium).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();

    await glutenFree.click();
    await expect(glutenFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '13.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();
    await expect(page.getByText('Gluten', {exact: true})).not.toBeVisible();

    await tomatoSauce.click();
    await expect(tomatoSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '13.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await bacon.click();
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '14.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await glutenFree.click();

    // Assert

    await expect(glutenFree).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '12.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
  });
});

test.describe('Lactose Free', () => {
  test.beforeEach(async ({page}) => {
    await page.route('*/**/api/v1/resource/product?type=pizza&pageNumber=0&pageSize=7', async route => {
      await route.fulfill({json: pizzas});
    });

    await page.goto('/pizzas');

    const openCustomPizza = page.getByTitle('Open Custom Pizza Builder').getByRole(`button`);
    await openCustomPizza.click();
  });

  test('givenLactoseFreeClick_whenNotLactoseFreeAndNoIngredients_thenUpdatePriceDisableCheeseAndDoNotAddLactoseOnNewIng', async ({page}) => {

    // Arrange

    const medium = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Medium'});
    const lactoseFree = page.getByRole('button', {name: 'Lactose free'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce', exact: true});
    const mozzarella = page.getByRole('button', {name: '100% Mozzarella', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act && Assert

    await medium.click();
    await lactoseFree.click();
    await expect(lactoseFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '13.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Parmesan Cheese', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Emmental Cheese'})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Goat Cheese', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Blue Cheese', exact: true})).toBeDisabled();

    await creamSauce.click();
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '13.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await mozzarella.click();
    await expect(mozzarella).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '13.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();
  });

  test('givenLactoseFreeClick_whenLactoseFreeAndIngredients_thenSoftResetAndUpdatePriceAndEnableCheeseAndAddLactoseOnNewIng', async ({page}) => {

    // Arrange

    const medium = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Medium'});
    const lactoseFree = page.getByRole('button', {name: 'Lactose free'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce', exact: true});
    const mozzarella = page.getByRole('button', {name: '100% Mozzarella', exact: true});
    const bacon = page.getByRole('button', {name: 'Smoked Bacon', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act

    await medium.click();
    await lactoseFree.click();
    await expect(lactoseFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '13.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();
    await expect(page.getByRole('button', {name: 'Parmesan Cheese', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Emmental Cheese'})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Goat Cheese', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Blue Cheese', exact: true})).toBeDisabled();

    await creamSauce.click();
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '13.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await mozzarella.click();
    await expect(mozzarella).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '13.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await bacon.click();
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '14.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3/9'})).toBeVisible();

    await lactoseFree.click();

    // Assert

    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();
    await expect(lactoseFree).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(creamSauce).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(mozzarella).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(bacon).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: 'Parmesan Cheese', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Emmental Cheese'})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Goat Cheese', exact: true})).toBeEnabled();
    await expect(page.getByRole('button', {name: 'Blue Cheese', exact: true})).toBeEnabled();

    await creamSauce.click();
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();
  });

  test('givenLactoseFreeClick_whenNotLactoseFreeAndIngredients_thenSoftResetAndUpdatePriceAndDisableCheeseAndDoNotAddLactoseOnNewIng', async ({page}) => {

    // Arrange

    const medium = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Medium'});
    const lactoseFree = page.getByRole('button', {name: 'Lactose free'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce', exact: true});
    const mozzarella = page.getByRole('button', {name: '100% Mozzarella', exact: true});
    const bacon = page.getByRole('button', {name: 'Smoked Bacon', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act

    await medium.click();
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();

    await creamSauce.click();
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await mozzarella.click();
    await expect(mozzarella).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await bacon.click();
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '12.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3/9'})).toBeVisible();

    await lactoseFree.click();

    // Assert

    await expect(page.getByRole('button', {name: '13.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();
    await expect(lactoseFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(creamSauce).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(mozzarella).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(bacon).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: 'Parmesan Cheese', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Emmental Cheese'})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Goat Cheese', exact: true})).toBeDisabled();
    await expect(page.getByRole('button', {name: 'Blue Cheese', exact: true})).toBeDisabled();

    await creamSauce.click();
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '13.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await bacon.click();
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '14.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();
  });
});

test.describe('Gluten free and Lactose Free', () => {
  test.beforeEach(async ({page}) => {
    await page.route('*/**/api/v1/resource/product?type=pizza&pageNumber=0&pageSize=7', async route => {
      await route.fulfill({json: pizzas});
    });

    await page.goto('/pizzas');

    const openCustomPizza = page.getByTitle('Open Custom Pizza Builder').getByRole(`button`);
    await openCustomPizza.click();
  });

  test('givenLactoseFreeClick_whenNotLactoseFreeAndGlutenFree_thenSoftRestAndUpdatePriceAndKeepGlutenFree', async ({page}) => {

    // Arrange

    const large = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Large'});
    const lactoseFree = page.getByRole('button', {name: 'Lactose free'});
    const glutenFree = page.getByRole('button', {name: 'Gluten free'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce', exact: true});
    const mozzarella = page.getByRole('button', {name: '100% Mozzarella', exact: true});
    const bacon = page.getByRole('button', {name: 'Smoked Bacon', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act

    await large.click();
    await expect(large).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '14.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();

    await glutenFree.click();
    await expect(glutenFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '18.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();
    await expect(page.getByText('Gluten', {exact: true})).not.toBeVisible();

    await creamSauce.click();
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: '18.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await mozzarella.click();
    await expect(mozzarella).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: '18.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await bacon.click();
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '20.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3/9'})).toBeVisible();

    await lactoseFree.click();

    // Assert

    await expect(page.getByText('Gluten', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '22.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();
    await expect(lactoseFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(glutenFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(creamSauce).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(mozzarella).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(bacon).not.toHaveCSS('color', 'rgb(249, 115, 22)');
  });

  test('givenLactoseFreeClick_whenLactoseFreeAndGlutenFree_thenSoftRestAndUpdatePriceAndKeepGlutenFree', async ({page}) => {

    // Arrange

    const large = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Large'});
    const lactoseFree = page.getByRole('button', {name: 'Lactose free'});
    const glutenFree = page.getByRole('button', {name: 'Gluten free'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce', exact: true});
    const mozzarella = page.getByRole('button', {name: '100% Mozzarella', exact: true});
    const bacon = page.getByRole('button', {name: 'Smoked Bacon', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act

    await large.click();
    await lactoseFree.click();
    await glutenFree.click();
    await expect(page.getByText('Gluten', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '22.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();

    await creamSauce.click();
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '22.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await mozzarella.click();
    await expect(mozzarella).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '22.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await bacon.click();
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '24.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3/9'})).toBeVisible();

    await lactoseFree.click();

    // Assert

    await expect(page.getByText('Gluten', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '18.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();
    await expect(lactoseFree).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(glutenFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(creamSauce).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(mozzarella).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(bacon).not.toHaveCSS('color', 'rgb(249, 115, 22)');
  });

  test('givenGlutenFreeClick_whenLactoseFreeAndNotGlutenFree_thenUpdatePriceAndRemoveGluten', async ({page}) => {

    // Arrange

    const large = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Large'});
    const lactoseFree = page.getByRole('button', {name: 'Lactose free'});
    const glutenFree = page.getByRole('button', {name: 'Gluten free'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce', exact: true});
    const mozzarella = page.getByRole('button', {name: '100% Mozzarella', exact: true});
    const bacon = page.getByRole('button', {name: 'Smoked Bacon', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act

    await large.click();
    await lactoseFree.click();
    await creamSauce.click();
    await mozzarella.click();
    await bacon.click();
    await expect(page.getByRole('button', {name: '20.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3/9'})).toBeVisible();
    await expect(lactoseFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(mozzarella).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    await glutenFree.click();

    // Assert

    await expect(page.getByText('Gluten', {exact: true})).not.toBeVisible();
    await expect(glutenFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '24.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3/9'})).toBeVisible();
    await expect(lactoseFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(mozzarella).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');
  });

  test('givenGlutenFreeClick_whenLactoseFreeAndGlutenFree_thenUpdatePriceAndAddGluten', async ({page}) => {

    // Arrange

    const large = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Large'});
    const lactoseFree = page.getByRole('button', {name: 'Lactose free'});
    const glutenFree = page.getByRole('button', {name: 'Gluten free'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce', exact: true});
    const mozzarella = page.getByRole('button', {name: '100% Mozzarella', exact: true});
    const bacon = page.getByRole('button', {name: 'Smoked Bacon', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();


    // Act

    await large.click();
    await lactoseFree.click();
    await glutenFree.click();
    await creamSauce.click();
    await mozzarella.click();
    await bacon.click();
    await expect(page.getByText('Gluten', {exact: true})).not.toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '24.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3/9'})).toBeVisible();
    await expect(glutenFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(lactoseFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(mozzarella).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');

    await glutenFree.click();

    // Assert

    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: '20.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3/9'})).toBeVisible();
    await expect(glutenFree).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(lactoseFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(mozzarella).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(bacon).toHaveCSS('color', 'rgb(249, 115, 22)');
  });
});

test.describe('No Lactose free and No gluten free', () => {
  test.beforeEach(async ({page}) => {
    await page.route('*/**/api/v1/resource/product?type=pizza&pageNumber=0&pageSize=7', async route => {
      await route.fulfill({json: pizzas});
    });

    await page.goto('/pizzas');

    const openCustomPizza = page.getByTitle('Open Custom Pizza Builder').getByRole(`button`);
    await openCustomPizza.click();
  });

  test('givenSwitchingLactoseAndNonLactoseIng_whenNotLactoseFree_thenUpdateLactoseAllergen', async ({page}) => {

    // Arrange

    const medium = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Medium'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce', exact: true});
    const tomatoSauce = page.getByRole('button', {name: 'Tomato Sauce', exact: true});
    const mozzarella = page.getByRole('button', {name: '100% Mozzarella', exact: true});
    const parmesan = page.getByRole('button', {name: 'Parmesan Cheese', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act && Assert

    await medium.click();
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();

    await creamSauce.click();
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible(); // !!!
    await expect(page.getByText('Lactose', {exact: true})).toBeVisible(); // !!

    await tomatoSauce.click();
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible(); // !!!
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible(); // !!

    await mozzarella.click();
    await expect(page.getByText('Lactose', {exact: true})).toBeVisible(); // !!
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await mozzarella.click();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible(); // !!
    await expect(page.getByRole('button', {name: '11.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await parmesan.click();
    await expect(page.getByText('Lactose', {exact: true})).toBeVisible(); // !!
    await expect(page.getByRole('button', {name: '12.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();
  });

  test('givenAddingAndRemovingIng_thenUpdatePriceAndQuantityAndLactoseAllergen', async ({page}) => {

    // Arrange

    const large = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Large'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce', exact: true});
    const doubleMozzarella = page.getByRole('button', {name: 'Double 100% Mozzarella', exact: true});
    const doubleBacon = page.getByRole('button', {name: 'Double Smoked Bacon', exact: true});
    const chicken = page.getByRole('button', {name: 'Chicken', exact: true});
    const goatCheese = page.getByRole('button', {name: 'Goat Cheese', exact: true});
    const onion = page.getByRole('button', {name: 'Onion', exact: true});
    const mushroom = page.getByRole('button', {name: 'Mushroom', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act && Assert

    await large.click();
    await expect(page.getByRole('button', {name: '14.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();

    await creamSauce.click();
    await expect(page.getByText('Lactose', {exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: '14.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await doubleMozzarella.click();
    await expect(page.getByRole('button', {name: '14.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await doubleBacon.click();
    await expect(page.getByRole('button', {name: '16.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3/9'})).toBeVisible();

    await chicken.click();
    await expect(page.getByRole('button', {name: '19.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '4/9'})).toBeVisible();

    await goatCheese.click();
    await expect(page.getByRole('button', {name: '21.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '5/9'})).toBeVisible();

    await onion.click();
    await expect(page.getByRole('button', {name: '24.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '6/9'})).toBeVisible();

    await mushroom.click();
    await expect(page.getByRole('button', {name: '26.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '7/9'})).toBeVisible();

    await onion.click();
    await expect(page.getByRole('button', {name: '24.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '6/9'})).toBeVisible();
  });
});

test.describe('Reset', () => {
  test.beforeEach(async ({page}) => {
    await page.route('*/**/api/v1/resource/product?type=pizza&pageNumber=0&pageSize=7', async route => {
      await route.fulfill({json: pizzas});
    });

    await page.goto('/pizzas');

    const openCustomPizza = page.getByTitle('Open Custom Pizza Builder').getByRole(`button`);
    await openCustomPizza.click();
  });

  test('givenReset_thenFullRest', async ({page}) => {

    // Arrange

    const reset = page.getByRole('button', {name: 'RESET'});
    const large = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Large'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce', exact: true});
    const doubleMozzarella = page.getByRole('button', {name: 'Double 100% Mozzarella', exact: true});
    const doubleBacon = page.getByRole('button', {name: 'Double Smoked Bacon', exact: true});
    const lactoseFree = page.getByRole('button', {name: 'Lactose free'});
    const glutenFree = page.getByRole('button', {name: 'Gluten free'});
    const onion = page.getByRole('button', {name: 'Onion', exact: true});
    const mushroom = page.getByRole('button', {name: 'Mushroom', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act

    await large.click();
    await glutenFree.click();
    await lactoseFree.click();
    await expect(page.getByText('Gluten', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '22.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();

    await creamSauce.click();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '22.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await doubleMozzarella.click();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '22.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await doubleBacon.click();
    await expect(page.getByRole('button', {name: '24.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3/9'})).toBeVisible();

    await onion.click();
    await expect(page.getByRole('button', {name: '27.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '4/9'})).toBeVisible();

    await mushroom.click();
    await expect(page.getByRole('button', {name: '29.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '5/9'})).toBeVisible();

    await expect(large).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(glutenFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(lactoseFree).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(creamSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(doubleMozzarella).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(doubleBacon).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(onion).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(mushroom).toHaveCSS('color', 'rgb(249, 115, 22)');

    await reset.click();

    // Assert

    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '0.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();
    await expect(large).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(glutenFree).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(lactoseFree).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(creamSauce).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(doubleMozzarella).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(doubleBacon).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(onion).not.toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(mushroom).not.toHaveCSS('color', 'rgb(249, 115, 22)');
  });
});

test.describe('Add', () => {
  test.beforeEach(async ({page}) => {
    await page.route('*/**/api/v1/resource/product?type=pizza&pageNumber=0&pageSize=7', async route => {
      await route.fulfill({json: pizzas});
    });

    await page.goto('/pizzas');

    const openCustomPizza = page.getByTitle('Open Custom Pizza Builder').getByRole(`button`);
    await openCustomPizza.click();
  });

  test('givenLessThanThreeIngredients_thenAddIsDisabled', async ({page}) => {

    // Arrange

    const add = page.getByLabel('Personalize however you like!').getByRole('button', { name: 'ADD' });
    const large = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Large'});
    const tomatoSauce = page.getByRole('button', {name: 'Tomato Sauce', exact: true});
    const doubleMozzarella = page.getByRole('button', {name: 'Double 100% Mozzarella', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act

    await large.click();
    await expect(page.getByRole('button', {name: '14.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();

    await tomatoSauce.click();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '14.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await doubleMozzarella.click();
    await expect(page.getByText('Lactose', {exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: '14.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    // Assert

    await expect(add).toBeDisabled();
    await expect(add).toHaveCSS('color', 'rgb(239, 68, 68)');
    await expect(page.getByRole('button', {name: '2/9'})).toHaveCSS('background-color', 'rgb(239, 68, 68)');
    await expect(large).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(tomatoSauce).toHaveCSS('color', 'rgb(249, 115, 22)');
    await expect(doubleMozzarella).toHaveCSS('color', 'rgb(249, 115, 22)');
  });

  test('givenMoreThanNineIngredients_thenAddIsDisabled', async ({page}) => {

    // Arrange

    const add = page.getByLabel('Personalize however you like!').getByRole('button', { name: 'ADD' });
    const large = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Large'});
    const tomatoSauce = page.getByRole('button', {name: 'Tomato Sauce', exact: true});
    const doubleMozzarella = page.getByRole('button', {name: 'Double 100% Mozzarella', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();

    // Act

    await large.click();
    await expect(page.getByRole('button', {name: '14.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();

    await tomatoSauce.click();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '14.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await doubleMozzarella.click();
    await expect(page.getByText('Lactose', {exact: true})).toBeVisible();
    await expect(page.getByRole('button', {name: '14.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await page.getByRole('button', {name: 'Parmesan Cheese', exact: true}).click();
    await page.getByRole('button', {name: 'Emmental Cheese', exact: true}).click();
    await page.getByRole('button', {name: 'Zucchini', exact: true}).click();
    await page.getByRole('button', {name: 'Black Olives', exact: true}).click();
    await page.getByRole('button', {name: 'Eggplant', exact: true}).click();
    await page.getByRole('button', {name: 'Pepperoni', exact: true}).click();
    await page.getByRole('button', {name: 'Beef', exact: true}).click();
    await page.getByRole('button', {name: 'York Ham', exact: true}).click();

    // Assert

    await expect(page.getByRole('button', {name: '34.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '10/9'})).toBeVisible();
    await expect(page.getByRole('button', {name: '10/9'})).toHaveCSS('background-color', 'rgb(239, 68, 68)');
    await expect(add).toBeDisabled();
    await expect(add).toHaveCSS('color', 'rgb(239, 68, 68)');
  });

  test('givenValidPizza_thenAdd', async ({page}) => {

    // Arrange

    const add = page.getByLabel('Personalize however you like!').getByRole('button', { name: 'ADD' });
    const medium = page.getByLabel('Personalize however you like!').getByRole('button', {name: 'Medium'});
    const creamSauce = page.getByRole('button', {name: 'Cream Sauce', exact: true});
    const mozzarella = page.getByRole('button', {name: '100% Mozzarella', exact: true});
    const doubleBacon = page.getByRole('button', {name: 'Double Smoked Bacon', exact: true});
    const chicken = page.getByRole('button', {name: 'Chicken', exact: true});
    const lactoseFree = page.getByRole('button', {name: 'Lactose free'});
    const glutenFree = page.getByRole('button', {name: 'Gluten free'});
    const onion = page.getByRole('button', {name: 'Onion', exact: true});
    const mushroom = page.getByRole('button', {name: 'Mushroom', exact: true});
    await expect(page.getByText('Gluten', {exact: true})).toBeVisible();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('dialog', {name: 'Personalize however you like!'})).toBeVisible();

    // Act

    await medium.click();
    await glutenFree.click();
    await lactoseFree.click();
    await expect(page.getByText('Gluten', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '15.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '0/9'})).toBeVisible();

    await creamSauce.click();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '15.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '1/9'})).toBeVisible();

    await mozzarella.click();
    await expect(page.getByText('Lactose', {exact: true})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '15.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '2/9'})).toBeVisible();

    await doubleBacon.click();
    await expect(page.getByRole('button', {name: '16.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '3/9'})).toBeVisible();

    await chicken.click();
    await expect(page.getByRole('button', {name: '18.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '4/9'})).toBeVisible();

    await onion.click();
    await expect(page.getByRole('button', {name: '19.50€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '5/9'})).toBeVisible();

    await mushroom.click();
    await expect(page.getByRole('button', {name: '21.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '6/9'})).toBeVisible();

    // Assert

    await expect(page.getByRole('button', {name: '21.00€'})).toBeVisible();
    await expect(page.getByRole('button', {name: '21.00€'})).toHaveCSS('background-color', 'rgb(249, 115, 22)');
    await expect(page.getByRole('button', {name: '6/9'})).toBeVisible();
    await expect(page.getByRole('button', {name: '6/9'})).toHaveCSS('background-color', 'rgb(249, 115, 22)');
    await expect(add).toBeEnabled();
    await expect(add).not.toHaveCSS('color', 'rgb(239, 68, 68)');
    await expect(add).toHaveCSS('color', 'rgb(249, 115, 22)');

    await add.click();

    await expect(page.getByRole('dialog', {name: 'Personalize however you like!'})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '21.00€'})).not.toBeVisible();
    await expect(page.getByRole('button', {name: '6/9'})).not.toBeVisible();

    const cartButton = page.getByTitle('Cart', {exact: true});
    await cartButton.click();

    await expect(page.getByTitle('My Pizza Medium').getByRole('img')).toBeVisible();
    await expect(page.getByRole('complementary').getByText('My Pizza')).toBeVisible();
    await expect(page.getByTitle('My Pizza Medium Format', {exact: true}).getByText('Medium')).toBeVisible();
    await expect(page.getByRole('complementary').getByTitle('My Pizza Medium Price').getByRole('button').getByText('21.00€')).toBeVisible();
    await expect(page.getByTitle('Increase My Pizza Medium Quantity')).toBeVisible();
    await expect(page.getByTitle('My Pizza Medium Quantity', {exact: true}).getByText('1')).toBeVisible();
    await expect(page.getByTitle('Decrease My Pizza Medium Quantity')).toBeVisible();
    await expect(page.getByTitle('Toggle My Pizza Medium Ingredients')).toBeVisible();
    const ingredients = page.getByRole('complementary').getByTitle('My Pizza Medium Ingredients', {exact: true}).getByText('Ingredients');
    await expect(ingredients).toBeVisible();
    await ingredients.click();
    await expect(page.getByText('Gluten free, Lactose free, Cream Sauce, 100% Mozzarella, Double Smoked Bacon, Chicken, Onion, Mushroom')).toBeVisible();
  });
});
