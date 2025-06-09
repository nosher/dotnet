/// <reference types="cypress" />

describe('nosher.net home page', () => {
  
    beforeEach(() => {
      cy.viewport(1100,660)
      cy.visit('http://10.1.203.1:8010/');
    })
    
    
    it('Check thumbnail grid is present', () => {
      cy.get('div#minigrid').find('img').should('have.length', 24);
    })
  

    it('Check grid thumbnail launches an album', () => {
        cy.get('div#minigrid').find('a').eq(0).click();
        cy.url().should('include', '/images/');
    })


    it('Check latest album links', () => {
        cy.get('ul.homelist').find('li').should('have.length', 9);
    })


    it('Check more albums link is present', () => {
        cy.get('ul.homelist').find('li').eq(8).should('contain', "more photo albums...");
    })


    it('Check more albums link launches photos', () => {
        cy.get('ul.homelist').find('a').eq(8).click();
        cy.url().should('include', '/images/');
    })


    it('Check more things links', () => {
        cy.get('div.grid').find('div.homegriditem').should('have.length', 9);
    })
    

    it('Check more things item 1 links to images', () => {
        cy.get('div.grid').find('div.homegriditem').eq(0).find('a').click();
        cy.url().should('include', '/images/');
    })


    it('Check search box does something', () => {
        cy.get('input#query').type('food{enter}');
        cy.url().should('include', '/search/?q=food');
    })


    it('Check footer text', () => {
        cy.get('footer').should('contain', "© nosher.net 1999-20")
    })


})  