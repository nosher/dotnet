/// <reference types="cypress" />

describe('nosher.net computer advert', () => {
  
  beforeEach(() => {
    cy.visit('http://10.1.203.1:8010/images/')
  })


  it('Check navmenu has links to photo years', () => {
    cy.get('p.navlink').should('have.length', 2).find('a').should(($link) => {
      expect($link.attr('href')).contains(/images/)
    })
  })


  it('Check page contains "Latest photos"', () => {
    cy.get('h1').should('have.length', 1).contains("Latest photos")
  })


  it('Check page contains links to photo albums', () => {
    cy.get('ul.index').should('have.length', 1).find('a').should(($link) => {
      expect($link.attr('href')).contains(/images/)
    })
  })


  it('Check there are a sensible number of latest albums', () => {
    cy.get('ul.index').should(($list) => {
      if ($list.find('a').length < 20 ) {
        throw new Error('Did not find latest photo albums')
      }
    })
  })


  it('Check footer contains correct text', () => {
    cy.get('footer').contains("photos@nosher.net")
  })


})
