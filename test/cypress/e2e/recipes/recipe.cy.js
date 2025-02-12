/// <reference types="cypress" />

describe('nosher.net recipes', () => {

    beforeEach(() => {
        cy.visit('http://10.1.203.1:8010/content/recipes/spagbol.html')
        // set viewport to over 1000 to avoid triggering mobile view
        cy.viewport(1100,660)
    })
  

    it('Recipe image is ', () => {
        cy.get('img.recimg').invoke('outerWidth').should('be.eq', 700);
    })


    it('Recipe contains an actual recipe', () => {
        cy.get('recipe-').should('have.length', 1)
    })


    it('Recipe contains a method recipe', () => {
        cy.get('method-').should('have.length', 1)
    })


    it('Recipe method contains items', () => {
        if(cy.get('method-').find('li').length < 5) {
            throw new Error('No or insufficient recipe method steps found')
        }
    })


    it('Recipe contains a serving section', () => {
        cy.get('serve-').should('have.length', 1)
    })


    it('Recipe contains a diet alternative section', () => {
        cy.get('diet-').should('have.length', 1)
    })


    it('Check footer contains correct text', () => {
        cy.get('footer').contains("recipes@nosher.net").contains("Last updated")
    })
})
  