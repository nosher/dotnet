/// <reference types="cypress" />

describe('nosher.net photo filters', () => {
  
  beforeEach(() => {
  })


  it('Check test filter', () => {
    cy.visit('http://10.1.203.1:8010/images/?title=Here%20Is%20A%20Test&group=Swan%20Inn%2C%20Brome%20Swan')
    cy.get('div.advert').find('h1').should('have.length', 1).contains('Here Is A Test photos')
  })


  it('Check test filter image', () => {
    cy.visit('http://10.1.203.1:8010/images/?title=Here%20Is%20A%20Test&group=Swan%20Inn%2C%20Brome%20Swan')
    cy.get('div.images_intro').find('img').should('have.length', 1).then($img => {
      expect($img.attr('alt')).contains('Here Is A Test')
    })
    cy.get('div.images_intro').find('p').should('have.length', 1).contains('Test text here')
  })


  it('Check filter results', () => {
    cy.visit('http://10.1.203.1:8010/images/?title=Here%20Is%20A%20Test&group=Swan%20Inn%2C%20Brome%20Swan')
    cy.get('ul.albums').then($list => {
      if ($list.find('li').length < 10 ) {
        throw new Error('Did not find filtered photo albums')
      }
    })
  })

  it('Check first filter is a valid result', () => {
    cy.visit('http://10.1.203.1:8010/images/?title=Here%20Is%20A%20Test&group=Swan%20Inn%2C%20Brome%20Swan')
    cy.get('ul.albums').find('li').first().find('a').click()
    cy.url().should('contain', '/images/2022/2022-02-17SwanEpilogue/')
  })


  it('Check test filter with no image', () => {
    cy.visit('http://10.1.203.1:8010/images/?title=Here%20Is%20A%20Test%20No%20Image&group=Swan%20Inn%2C%20Brome%20Swan')
    cy.get('div.images_intro').find('img').should('have.length', 0)
    cy.get('div.images_intro').find('p').should('have.length', 1).contains('Imageless test text here')
  })

  
  it('Check filter with no intro or valid key works', () => {
    cy.visit('http://10.1.203.1:8010/images/?title=No%20File&group=NoMatch')
    cy.get('ul.albums').find('li').should('have.length', 0)
    cy.get('div.images_intro').should('have.length', 0)
    cy.get('div.advert').find('h1').should('have.length', 1).contains('No File photos')
  })


})
