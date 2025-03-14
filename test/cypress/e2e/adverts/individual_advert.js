/// <reference types="cypress" />

describe('nosher.net computer adverts - individual', () => {
  
  beforeEach(() => {
    cy.visit('http://10.1.203.1:8010/archives/computers/acorn_sparkjet_percw_aug83')
  })
 

  it('Check display of advert sidebar', () => {
    cy.get('sidebar')
      .should('have.length', 1)
    if(cy.get('sidebar').find('div.adthumb').length == 0) {
      throw new Error('No adverts linked in sidebar')
    }
  })


  it('Check each advert sidebar has a link', () => {
    cy.get('div.adthumb')
      .each(($item) => {
        if ($item.find('a').length !== 1) {
          throw new Error('Did not find advert anchor')
        }
    })
  })


  /*
   * Visit an Acorn advert then link to the first advert in the adverts sidebar. 
   * This is unlikely to change in the future as this literally is Acorn's first known advert
  */
  it('Check first advert links to a valid page', () => {
    cy.get('div.adthumb').first().find('a').then(function ($a) {
      const href = $a.prop('href')
      cy.visit(href)
      cy.url().should('include', 'acorn_firstadvert')
    })
  });


  it('Check advert entry to self in sidebar is disabled', () => {
    cy.get('div.adthumb_dim').should('have.length', 1).find('a').should('have.length', 0)
    cy.get('div.adthumb_dim').find('img').should('have.prop', 'src')
      .and('include', 'acorn_sparkjet_percw_aug83')
  });


  it('Check advert has at least two sources', () => {
    cy.get('section.sources').should(($sources) => {
      if ($sources.find('div.source').length < 2 ) {
        throw new Error('Did not enough sources')
      }
    })
  })


  it('Check navmenu has links to companies', () => {
    cy.get('p.navlink').should('have.length', 1).should(($nav) => {
      if ($nav.find('a').length < 20 ) {
        throw new Error('Did not find company links')
      }
    })
  })


  it('Check inter-advert navlinks for non-first-or-last advert', () => {
    cy.get('p.nav').should('have.length', 1).should(($nav) => {
      if ($nav.find('a').length != 9 ) {
        throw new Error('Incorrect number of inter-adverts navlinks')
      }
    })
  })
  

  it('Check inter-advert navlinks for first advert', () => {
    cy.get('div.adthumb').first().find('a').then(function ($a) {
      const href = $a.prop('href')
      cy.visit(href)
    })
    cy.get('p.nav').should('have.length', 1).should(($nav) => {
      if ($nav.find('a').length != 8 ) {
        throw new Error('Incorrect number navlinks (should not have previous advert link)')
      }
    })
  })


  it('Check company logo is present: portrait version (logo and title side by side)', () => {
    // should be the portrait variant
    cy.get('div#clogo').should('have.length', 1).find('img').should('have.prop', 'src')
      .and('include', 'images/logos/Acorn.webp')
    cy.get('div#clogo').find('img.companylogo_port').should('have.prop', 'alt')
      .and('include', 'Acorn company logo')
  })


  it('Check company logo is not preset', () => {
    // the company ComX does not have an apparent logo
    cy.visit('http://10.1.203.1:8010/archives/computers/pcw_1983-06_021_alsycomx35')
    cy.get('div#sidebyside').should('have.length', 0)
    cy.get('img.companylogo').should('have.length', 0)
    cy.get('img.companylogo_port').should('have.length', 0)
  })


  it('Check company logo is present: landscape version', () => {
    // should be the landscape variant
    cy.visit('http://10.1.203.1:8010/archives/computers/comm_012')
    cy.get('div#sidebyside').should('have.length', 0)
    cy.get('img.companylogo').should('have.length', 1).should('have.prop', 'src')
      .and('include', 'images/logos/Commodore.webp')
    cy.get('img.companylogo').should('have.prop', 'alt')
      .and('include', 'Commodore company logo')
  })


  it('Check navmenu first link is Acorn', () => {
    cy.get('p.navlink').find('a').first().should('have.prop', 'href')
        .and('include', 'value=Acorn')
  })


  it('Check body contains correct title', () => {
    cy.get('section.advert h1').contains("Acorn Advert")
  })


  it('Check footer contains correct text', () => {
    cy.get('footer').contains("microhistory@nosher.net")
  })


  it('Check date created is present', () => {
    cy.get('p.updated').contains("Date created: 25 January 2025")
  })


  it('Check main image properties', () => {
    cy.get('div.zoomer').should('have.length', 1).find('img').should('have.length', 1).first().should('have.attr', 'src')
        .and('include', 'archives/computers/images/acorn_sparkjet_percw_aug83-m.webp')
    cy.get('div.zoomer').find('img').should('have.attr', 'style')
        .and('include', 'aspect-ratio:')
    cy.get('div.zoomer').find('img').should('have.attr', 'alt')
        .and('include', 'Acorn Advert: Join the jet set')
  })


  it('Check main body text', () => {
    cy.get('div.liner').find('p').should(($para) => {
      if (($para).length < 4 ) {
        throw new Error('Insufficient paragraphs shown')
      }
    })
  })

  /*
   * The following relative links might change if the order of adverts changes, but
   * as they're early they probably won't
  */  
  it('Check next advert link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/acorn_firstadvert_praccomp_may79')
    cy.get('p.nav').find('a').contains('next advert').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', 'pcw_1980-06-00_002_msi')
    })
  })


  it('Check previous advert link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/pcw_1980-06-00_002_msi')
    cy.get('p.nav').find('a').contains('previous advert').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', 'acorn_firstadvert_praccomp_may79')
    })
  })


  it('Check next Acorn advert link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/acorn_firstadvert_praccomp_may79')
    cy.get('p.nav').find('a').contains('next Acorn advert').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', 'pcw_1979-09_022')
    })
  })


  it('Check previous Acorn advert link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/pcw_1979-09_022')
    cy.get('p.nav').find('a').contains('previous Acorn advert').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', 'acorn_firstadvert_praccomp_may79')
    })
  })


  // the following three tests use a null/404 advert handler which can optionally
  // be told to generate certain relative updated dates. These tests also 
  // effectively test the presence of the 404 page for adverts, as "foo" does
  // not exist as a real advert.

  it('Check date created, updated should not be present', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/foo?sameday')
    cy.get('p.updated').contains('Date created: 01 January 2025')
    cy.get('p.updated').contains('Last updated').should('not.exist')
  })
  

  it('Check date created, updated should be present', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/foo?twoday')
    cy.get('p.updated').contains('Date created: 01 January 2025')
    cy.get('p.updated').contains('Last updated: 03 January 2025')
  })


  it('Check broken modified date, updated should not be present', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/foo?yesterday')
    cy.get('p.updated').contains('Date created: 01 January 2025')
    cy.get('p.updated').contains('Last updated').should('not.exist')
  })


  it('Check wiki-style links have been created', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/comp_today_1981-09_042')
    cy.get('a[data-link]').should(($links) => {
      if ($links.length == 0 ) {
        throw new Error('Did not find any wiki-style links')
      }
    })
    cy.get(`a[data-link="adve_024"]`).first().then(function($link) {
      cy.wrap($link).should('have.text', 'the Atom')
        .should('have.attr', "href").and('include', 'adve_024')
    })
    cy.get(`a[data-link="Sinclair"]`).first().then(function($link) {
      cy.wrap($link).should('have.text', 'Sinclair')
      .should('have.attr', "href").and('include', '/archives/computers?type=source&value=Sinclair')
    })
    cy.get(`a[data-link="https://www.computinghistory.org.uk/det/4236/The-Mighty-Micro"]`).first().then(function($link) {
      cy.wrap($link).should('have.text', 'The Mighty Micro')
      .should('have.attr', "href").and('include', 'https://www.computinghistory.org.uk/det/4236/The-Mighty-Micro')
    })
  })
  

})
