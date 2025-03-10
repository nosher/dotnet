/// <reference types="cypress" />

describe('nosher.net computer adverts - index', () => {
  beforeEach(() => {
    cy.visit('http://10.1.203.1:8010/archives/computers/')
  })

  it('Displays fifteen advert items by default', () => {
    cy.get('archiveitem')
      .should('have.length', 15)
      .each(($item) => {
        cy.wrap($item).children('archivethumb').should('have.length', 1)
        cy.wrap($item).children('archivethumb').find('a').should('have.length', 1).should('have.attr', 'href')
        cy.wrap($item).children('archivedescription').should('have.length', 1)
        cy.wrap($item).children('archivedescription').find('a').should('have.length', 2)
        cy.wrap($item).children('archivedescription').find('h3').should('have.length', 1)
        cy.wrap($item).children('archivedescription').find('h4').should('have.length', 1)
    })
  })

  it('Displays an advert when first item in list is clicked', () => {
    cy.get('archiveitem').first().find('archivethumb').click()
    cy.get('section.advert').find('p.updated').should('have.length', 1)
    cy.get('section.advert')
    .should(($advert) => {
      if ($advert.find('p.nav').length !== 1) {
        throw new Error('Did not find top navigation')
      }
      if ($advert.find('h2').length !== 1) {
        throw new Error('Did not find magazine source')
      }
      if ($advert.find('h3').length !== 1) {
        throw new Error('Did not find advert title')
      }
      if ($advert.find('div.liner').length !== 1) {
        throw new Error('Did not find advert liner div')
      }
      if ($advert.find('div.liner').find('p').length == 0) {
        throw new Error('Did not find any advert content')
      }
      if ($advert.find('p.navbottom').length != 1) {
        throw new Error('Did not find bottom navigation')
      }
    })
  })


  it('Check company link goes to company-specific adverts', () => {
    cy.get('p.navlink').first().find('a').first().invoke('text').then(($text) => {
      cy.get('p.navlink').first().find('a').first().click()
      cy.url().should('contain', 'type=source&value=' + $text.trim())
    })
  })


  it('Check company-specific adverts all contains ads for specified company', () => {
    cy.get('p.navlink').first().find('a').first().invoke('text').then(($text) => {
      cy.get('p.navlink').first().find('a').first().click()
      cy.get('archivedescription').should('have.attr', 'data-company').should('contain', $text)
    })
  })


  it('Check company-specific adverts do not show company name', () => {
    cy.get('p.navlink').first().find('a').first().invoke('text').then(($text) => {
      cy.get('p.navlink').first().find('a').first().click()
      cy.get('archivedescription').find('h3').should('have.length', 0)
    })
  })


  it('Check next 15 adverts are not the same', () => {
    const firstAds = []
    const secondAds = []
    cy.get('archivethumb').each(($thumb) => {
      firstAds.push($thumb.find('a').first().prop('href'))
    })
    cy.get('p.nav').first().find('a').last().click()
    cy.get('archivethumb').each(($thumb) => {
      secondAds.push($thumb.find('a').first().prop('href'))
    }).then(() => {
      expect(firstAds).to.not.deep.equal(secondAds)
    })
  })


  it('Check adverts by year', () => {
    cy.get('p.nav').find('a').contains('by year').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.get('section.archives').find('h3').each(($header) => {
        cy.wrap($header).invoke('text').should('match', /^[0-9]{4}$/)
      })
    })
  })


  it('Check linked advert is correct year', () => {
    // meh - there's a chance this could be right by accident, but we don't want
    // to have to check all 400 adverts or whatever
    cy.visit('http://10.1.203.1:8010/archives/computers/years/')
    cy.get('section.archives').find('h3').first().invoke('text').then(($text) => {
      const year = $text
      cy.get('section.archives').find('div#yearindex').find('a').first().then(($link) => {
        const href = $link.prop('href')
        cy.visit(href)
        cy.get('h1.logo').first().invoke('text').should('include', year)
      })
    })
  })


  it('Check advert A-Z index', () => {
    // a-z index initially goes to the "A" section
    cy.get('p.nav').find('a').contains('a-z index').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.get('div.catindex').should('have.length', 1).find('p').eq(1).find('b').should('have.text', 'A')
    })
  })
 
 
  it('Check link to single-advert company goes straight to advert', () => {
    cy.get('p.navlink').find('a').contains('Asda').click()
    cy.get('section.advert').should('have.length', 1)
  })


  it('Check link to multi-advert company goes to a list', () => {
    cy.get('p.navlink').find('a').contains('Amstrad').click()
    cy.get('section.archives').should('have.length', 1)
  })


  it('Check correct title is present in the Acorn adverts list', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/?type=source&value=Acorn')
    cy.get('h1.logo').should('have.length', 1).should('have.text', 'Acorn adverts')
  })


  it('Check company logo is present in the Acorn adverts list', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/?type=source&value=Acorn')
    cy.get('div#clogo').should('have.length', 1).find('img').should('have.prop', 'src')
      .and('include', 'images/logos/Acorn.webp')
    cy.get('div#clogo').find('img.companylogo_port').should('have.prop', 'alt')
      .and('include', 'Acorn company logo')
  })


})
