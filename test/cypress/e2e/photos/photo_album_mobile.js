/// <reference types="cypress" />

describe('nosher.net photo album mobile', () => {
  
  beforeEach(() => {
    // set viewport to 320,480 to trigger mobile view
    cy.viewport('samsung-s10', 'portrait')
    cy.visit('http://10.1.203.1:8010/images/2025/2025-01-19WalkAroundDebenham/')
  })
  
  
  it('Check desktop viewer and photo strip are hidden viewer mode', () => {
    cy.get('article.thumb').first().click()
    cy.get('#viewer').should('not.be.visible')
    cy.get('section#strip').should('not.be.visible')
  })


  it('Click first photo to open viewer', () => {
    cy.get('article.thumb').first().click()
    cy.get('#mobile_viewer').should('be.visible')
  })


  it('Click fourth photo is in view after open viewer from fourth thumbnail', () => {
    cy.get('article.thumb').eq(4).find('a').click()
    cy.get('#mobile_viewer').should('be.visible')
    cy.get("div#mphoto_4").then( $el => {
      const bottom = Cypress.$( cy.state("window") ).height();
      const rect = $el[0].getBoundingClientRect();
      expect( rect.top ).to.be.eq(0);
      expect( rect.bottom ).to.be.lessThan(bottom);
  });
  })

})
