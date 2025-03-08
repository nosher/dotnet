/// <reference types="cypress" />

describe('nosher.net computer advert', () => {
  
  beforeEach(() => {
    // set viewport to 320,480 to trigger mobile view
    cy.viewport('samsung-s10', 'portrait')
    
  })

  it('Check display of company logo - landscape', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cal_wordproc_percw_nov82')
    cy.get('img.companylogo').should('have.length', 1).should(el => expect(el.width()).eq(180))
    cy.get('img.companylogo_port').should('have.length', 0)
  })


  it('Check display of company logo - portrait (logo and title side by side)', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/pcw_1982_12_004a')
    cy.get('div#clogo').should('have.length', 1)
    cy.get('img.companylogo_port').should('have.length', 1).should(el => expect(el.width()).eq(80))
    cy.get('img.companylogo').should('have.length', 0)
  })
  
})
