/// <reference types="cypress" />

describe('nosher.net computer ads index', () => {
  
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


  it('Check advert has two sources', () => {
    cy.get('section.sources').find('div.source').should('have.length', 2)
  })


  it('Check navmenu has links to companies', () => {
    cy.get('p.navlink').should('have.length', 1).should(($nav) => {
      if ($nav.find('a').length < 20 ) {
        throw new Error('Did not find company links')
      }
    })
  })


  /*
   *<p class="nav">
        <a href="/archives/computers">adverts home</a> | <a href="/archives/computers/index">a-z index</a> | <a href="/archives/computers/links/">industry connections</a> | <a href="/archives/computers/timelines">timelines</a> | <a href="/archives/computers/years/">by year</a>  | <a href="pcn_1983-08-25_v1_no25_002">next Acorn advert</a> | <a href="comm_004-a">previous Acorn advert</a> | <a href="itcs_andromeda_percw_aug83">previous advert</a> | <a href="adve_020">next advert</a>

    </p>
  */
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


  it('Check navmenu first link is Acorn', () => {
    cy.get('p.navlink').find('a').first().should('have.prop', 'href')
        .and('include', 'value=Acorn')
  })


  it('Check footer contains correct text', () => {
    cy.get('footer').contains("microhistory@nosher.net").contains("Last updated")
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

})
